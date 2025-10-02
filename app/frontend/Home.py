import streamlit as st

st.markdown('''
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        height: 80vh;
        text-align: center;
    ">
        <h1 style="
            margin: 0;
            padding: 0;
            font-size: 3.5rem;
            font-weight: bold;
        ">
            Welcome to RAG for the Books 📚
        </h1>
    </div>
''', unsafe_allow_html=True)

st.sidebar.info('Develop by: Cyrus Gahatraj')