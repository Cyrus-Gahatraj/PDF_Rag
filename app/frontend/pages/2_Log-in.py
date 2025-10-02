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

st.title('Log-in')
email = st.text_input('Email')
password = st.text_input('Password', type='password')

if st.button('Login'):
    if email and password:
        result = login(email, password)
        if 'access_token' in result:
            st.success("Login successful!")
            st.session_state.access_token = result['access_token']
            st.session_state.logged_in = True
            st.session_state.email = email
            st.sidebar.info(f"Token: {result['access_token']}")
        else:
            st.error(f"Login failed: {result.get('error', 'Unknown error')}")
    else:
        st.warning("Please enter all values: Email and Password")