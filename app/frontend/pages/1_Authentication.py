import streamlit as st
import requests

URL = 'http://localhost:8000'

def login(email, password):
    response = requests.post(
        f"{URL}/auth/log-in",
        data={'username': email, 'password': password}  
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json().get('detail')}

def signup(email, username, password):
    response = requests.post(
        f"{URL}/auth/sign-up",
        json={'email': email, 
              'username': username,
              'password': password}  
    )
    if response.status_code == 201:
        return response.json()
    else:
        return {"error": response.json().get('detail')}

def evaluate_result(result, email, logged_in=True):
    if 'access_token' in result:
        st.session_state.access_token = result['access_token']
        st.session_state.logged_in = logged_in
        st.session_state.email = email
        with st.sidebar.expander('Token', expanded=False):
            st.write(result['access_token'])
    else:
        raise Exception('Invalid Password')

st.markdown(
    """
    <style>
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔐 Authentication Portal")
st.write("Welcome! Please **Sign up** or **Log in** below.")

tab1, tab2 = st.tabs(["📝 Sign Up", "🔑 Log In"])

with tab1:
    st.subheader("Create a new account")
    col1, col2 = st.columns([1,1])
    with col1:
        email = st.text_input("Email", key="signup_email")
    with col2:
        username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Sign Up", key="signup_btn"):
        if email and username and password:
            result = signup(email, username, password)
            if 'id' in result:
                st.session_state.user_id = result['id']
                st.session_state.user_email = result['email']
                st.session_state.user_name = result['username']

                result = login(email, password)
                try:
                    evaluate_result(result, email)
                    st.success("✅ Sign up successful!")
                except Exception as e:
                    st.error(f"Error occur in log-in: {e}")
            else:
                st.error(f"Sign up failed: {result.get('error', 'Unknown error')}")
        else:
            st.warning("⚠️ Please fill all fields.")

with tab2:
    st.subheader("Access your account")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log In", key="login_btn"):
        if email and password:
            result = login(email, password)
            try:
                evaluate_result(result, email)
                st.success("Login successful! 🎉")
            except Exception as e:
                st.error(f"Error occur: {e}")
        else:
            st.warning("⚠️ Please fill all fields.")
