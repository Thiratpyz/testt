import av
import os
import sys
import streamlit as st
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
from aiortc.contrib.media import MediaRecorder

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(BASE_DIR)

from utils import get_mediapipe_pose
from process_frame import ProcessFrame
from thresholds import get_thresholds_beginner
from supabase import create_client, Client

# Retrieve the token from query parameters
token = ()
try:
    token = st.query_params.token
except:
    pass

# Initialize connection to Supabase
@st.cache_resource
def init_connection():
    url = "https://ucebadbqppftdjpaqfat.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVjZWJhZGJxcHBmdGRqcGFxZmF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTg5ODA2NzcsImV4cCI6MjAzNDU1NjY3N30._J7KGK8HaVdIfAfNqHWyCcbg_0pw_GXDp4XG_mJgOsE"
    return create_client(url, key)

supabase = init_connection()

# Perform query and convert to serializable format
@st.cache_data(ttl=600)
def get_data():
    response = supabase.table("user_data").select("*").execute()
    return response.data

# Query for user ID associated with the token
result = supabase.table('user_history').select('user_name').eq('token', token).execute()
result2 = supabase.table('user_history').select('user_gesture').eq('token', token).execute()
result3 = supabase.table('user_history').select('gesture_pic_path').eq('token', token).execute()

if result.data:
    st.title(f"Hello! {result.data[0]['user_name']},")
    st.header(f"Welcome to {result2.data[0]['user_gesture']} Therapy")
else:
    st.subheader(':red[! There is no any token embedded in url !]')
    
RTC_CONFIGURATION = ({
    "iceServers": [
        {"urls": "relay1.expressturn.com:3478", "username": "efN5UEXYAUXKY7AJYR", "credential": "H5dxcI4wCwLjdSUS"}
    ]
})

thresholds = get_thresholds_beginner()

live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)
# Initialize face mesh solution
pose = get_mediapipe_pose()


if 'download' not in st.session_state:
    st.session_state['download'] = False

output_video_file = f'output_live.flv'

  

def video_frame_callback(frame: av.VideoFrame):
    frame = frame.to_ndarray(format="rgb24")  # Decode and get RGB frame
    frame, _ = live_process_frame.process(frame, pose)  # Process frame
    return av.VideoFrame.from_ndarray(frame, format="rgb24")  # Encode and return BGR frame


def out_recorder_factory() -> MediaRecorder:
        return MediaRecorder(output_video_file)


ctx = webrtc_streamer(
                        key="Squats-pose-analysis",
                        video_frame_callback=video_frame_callback,
                        rtc_configuration=RTC_CONFIGURATION,  # Add this config
                        media_stream_constraints={"video": {"width": {'min':480, 'ideal':480}}, "audio": False},
                        video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
                        out_recorder_factory=out_recorder_factory
                    )



if st.button("Back to YUEDMAI"):
    st.markdown("""
        <meta http-equiv="refresh" content="0; url='https://yuedmaitest.vercel.app/'" />
        """, unsafe_allow_html=True
    )

