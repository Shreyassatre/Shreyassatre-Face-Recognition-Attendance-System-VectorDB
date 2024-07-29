import streamlit as st
import requests
import cv2
import io
import logging
from PIL import Image
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

BACKEND_URL = "http://localhost:8000"

st.title("Face Recognition System")

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'role' not in st.session_state:
    st.session_state.role = None

def capture_image():
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            logging.error("Failed to capture image from webcam")
            return None
    except Exception as e:
        logging.error(f"Error capturing image: {str(e)}")
        return None

def image_to_file(image):
    if image is None:
        logging.error("Cannot convert None image to file")
        return None
    try:
        pil_image = Image.fromarray(image)
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)  # move to the beginning of file
        return img_byte_arr
    except Exception as e:
        logging.error(f"Failed to encode image: {str(e)}")
        return None

def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        if username and password:
            with st.spinner("Logging in..."):
                response = requests.post(f"{BACKEND_URL}/login", data={"username": username, "password": password})
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.access_token = result['access_token']
                    st.session_state.username = username
                    st.session_state.role = "admin" if username == "admin" else "user"
                    st.success(f"Logged in as {username}")
                else:
                    st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
        else:
            st.warning("Please provide both username and password.")

def admin_login():
    st.sidebar.subheader("Admin Login")
    admin_username = st.sidebar.text_input("Admin Username", key="admin_login_username", value="admin")
    admin_password = st.sidebar.text_input("Admin Password", type="password", key="admin_login_password", value="admin")
    
    if st.sidebar.button("Admin Login"):
        if admin_username and admin_password:
            with st.spinner("Logging in..."):
                response = requests.post(f"{BACKEND_URL}/login", data={"username": admin_username, "password": admin_password})
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.access_token = result['access_token']
                    st.session_state.username = admin_username
                    st.session_state.role = "admin"
                    st.success(f"Logged in as {admin_username}")
                else:
                    st.error(f"Admin login failed: {response.json().get('detail', 'Unknown error')}")
        else:
            st.warning("Please provide both username and password.")

def list_users():
    st.subheader("List Users")
    if st.session_state.role != "admin":
        st.warning("You do not have permission to view this page.")
        return

    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{BACKEND_URL}/admin/users/", headers=headers)
    if response.status_code == 200:
        users = response.json()
        st.write(users)
    else:
        st.error(f"Failed to fetch users: {response.json().get('detail', 'Unknown error')}")

def get_attendance():
    st.subheader("Get Attendance")
    if st.session_state.role != "admin":
        st.warning("You do not have permission to view this page.")
        return

    date = st.date_input("Select date")
    if st.button("Get Attendance"):
        date_str = date.strftime("%Y-%m-%d")
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(f"{BACKEND_URL}/admin/attendance/{date_str}", headers=headers)
        if response.status_code == 200:
            attendance = response.json()
            st.write(attendance)
        else:
            st.error(f"Failed to fetch attendance: {response.json().get('detail', 'Unknown error')}")

def list_attendance_sheets():
    st.subheader("List Attendance Sheets")
    if st.session_state.role != "admin":
        st.warning("You do not have permission to view this page.")
        return

    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{BACKEND_URL}/admin/attendance-sheets/", headers=headers)
    if response.status_code == 200:
        attendance_sheets = response.json()
        st.write(attendance_sheets)
    else:
        st.error(f"Failed to fetch attendance sheets: {response.json().get('detail', 'Unknown error')}")

def list_attendance_sheets_range():
    st.subheader("List Attendance Sheets by Date Range")
    if st.session_state.role != "admin":
        st.warning("You do not have permission to view this page.")
        return

    start_date = st.date_input("Select start date", value=(datetime.today() - timedelta(days=7)))
    end_date = st.date_input("Select end date", value=datetime.today())
    if st.button("Get Attendance Sheets"):
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(f"{BACKEND_URL}/admin/attendance-sheets-range", headers=headers, params={"start_date": start_date_str, "end_date": end_date_str})
        if response.status_code == 200:
            attendance_sheets = response.json()
            st.write(attendance_sheets)
        else:
            st.error(f"Failed to fetch attendance sheets: {response.json().get('detail', 'Unknown error')}")

def register():
    username = st.text_input("Enter username to register:", key="register_username")
    
    if st.button("Register"):
        if not img_data:
            st.warning("Please click the photo first")
        if username:
            with st.spinner("Capturing image..."):
                image = capture_image()
            if image is not None:
                image_file = image_to_file(image)
                if image_file:
                    files = {'image_data': ('image.jpg', image_file, 'image/jpeg')}
                    data = {'username': username}
                    with st.spinner("Registering..."):
                        response = requests.post(f"{BACKEND_URL}/register", files=files, data=data)
                    if response.status_code == 200:
                        st.success(response.json()['message'])
                    else:
                        st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
                else:
                    st.error("Failed to process image.")
            else:
                st.error("Failed to capture image. Please make sure your webcam is working and try again.")
        else:
            st.warning("Please provide a username.")

def mark_attendance():
    if st.button("Mark Attendance"):
        if not img_data:
            st.warning("Please click the photo first")
        with st.spinner("Capturing image..."):
            image = capture_image()
        if image is not None:
            image_file = image_to_file(image)
            if image_file:
                files = {'image_data': ('image.jpg', image_file, 'image/jpeg')}
                with st.spinner("Logging in..."):
                    response = requests.post(f"{BACKEND_URL}/mark-attendance", files=files)
                if response.status_code == 200:
                    result = response.json()
                    if 'user_id' in result:
                        st.session_state.user_id = result['user_id']
                        st.session_state.username = result['username']
                        st.success(f"Attendance marked as {result['username']} (Similarity score: {result['similarity_score']:.2f})")
                    else:
                        st.warning(result['message'])
                else:
                    st.error(f"Attendance marking failed: {response.json().get('detail', 'Unknown error')}")
            else:
                st.error("Failed to process image.")
        else:
            st.error("Failed to capture image. Please make sure your webcam is working and try again.")

if 'access_token' not in st.session_state:
    admin_login()
else:
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Home", "List Users", "Get Attendance", "List Attendance Sheets", "List Attendance Sheets by Date Range", "Admin Login"])

    if choice == "Home":
        col1, col2 = st.columns(2)

        with col1:
            img_data = st.camera_input("Webcam Feed", key="camera_feed")
        with col2:
            operation = st.radio("Choose Operation", ("Register", "Mark Attendance"))
            if operation == "Register":
                register()
            elif operation == "Mark Attendance":
                mark_attendance()
    elif choice == "List Users":
        list_users()
    elif choice == "Get Attendance":
        get_attendance()
    elif choice == "List Attendance Sheets":
        list_attendance_sheets()
    elif choice == "List Attendance Sheets by Date Range":
        list_attendance_sheets_range()
    elif choice == "Admin Login":
        admin_login()
