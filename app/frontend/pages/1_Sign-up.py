import streamlit as st
import requests

URL = 'http://localhost:8000'

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

st.title('Sign-up')
email = st.text_input('Email')
username = st.text_input('Username')
password = st.text_input('Password', type='password')

if st.button('Signup'):
    if email and username and password:
        result = signup(email, username, password)
        if 'id' in result:
            st.success("Sign up successful!")
            st.session_state.user_id = result['id']
            st.session_state.user_email = result['email']
            st.session_state.user_name = result['username']

            st.sidebar.info("Please login with your new account to get an access token.")
        else:
            st.error(f"Sign up failed: {result.get('error', 'Unknown error')}")
    else:
        st.warning("Please enter all values: Email, Username, and Password.")