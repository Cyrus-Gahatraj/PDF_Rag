import streamlit as st
import requests

URL = 'http://localhost:8000'

# --------- Auth Guard --------- #
if 'access_token' not in st.session_state or not st.session_state.get('logged_in'):
    st.warning('Please login first! 🔑')
    st.stop()

# Headers will be defined dynamically in functions to ensure access_token is available

# --------- Global CSS Styling --------- #
st.markdown('''
<style>
/* File uploader styling */
.stFileUploader p {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 8px;
}

/* Indented labels */
.indented-text {
    padding-left: 50px; 
    font-size: 18px;
    font-weight: 500;
}

/* Chunk slider styling */
div[data-baseweb='slider'] > div {
    padding: 16px 10px;
}
.css-1aumxhk {  /* enlarge number labels */
    font-size: 18px !important;
    font-weight: bold !important;
}
.stSlider {
    margin-top: 20px;
    margin-bottom: 30px;
}
.stSlider label {
    font-size: 18px;
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 20px;
}
</style>
''', unsafe_allow_html=True)

# --------- Cached PDF Fetch --------- #
@st.cache_data(ttl=60)
def get_pdfs():
    try:
        headers = {
            'Authorization': f'Bearer {st.session_state.access_token}'
        }
        with st.spinner('📂 Fetching PDFs...'):
            respond = requests.get(f'{URL}/documents', headers=headers)
        if respond.status_code == 200:
            return respond.json()
        else:
            st.error(f'Failed to fetch PDFs: {respond.status_code}')
            return []
    except Exception as e:
        st.error(f'Error fetching PDFs: {str(e)}')
        return []

# --------- API Helpers --------- #
def upload_pdf(pdf_file, chunk_size=1000):
    try:
        headers = {
            'Authorization': f'Bearer {st.session_state.access_token}'
        }
        file = {'file': (pdf_file.name, pdf_file.getvalue(), pdf_file.type)}
        data = {'chunk_size': chunk_size}
        respond = requests.post(
            f'{URL}/documents/upload',
            files=file,
            data=data,
            headers=headers
        )
        return respond.json()
    except Exception as e:
        return {'detail': f'Upload failed: {str(e)}'}

def delete_pdf(pdf_id):
    try:
        headers = {
            'Authorization': f'Bearer {st.session_state.access_token}'
        }
        respond = requests.delete(f'{URL}/documents/{pdf_id}', headers=headers)
        return respond
    except requests.exceptions.ConnectionError as e:
        st.error(f'Connection failed: Cannot reach server at {URL}. Make sure the backend server is running.')
        return None
    except requests.exceptions.Timeout as e:
        st.error(f'Request timeout: Server took too long to respond')
        return None
    except requests.exceptions.RequestException as e:
        st.error(f'Request failed: {str(e)}')
        return None
    except Exception as e:
        st.error(f'Unexpected error: {str(e)}')
        return None

def ask_query(document_id: int, question: str):
    try:
        headers = {
            'Authorization': f'Bearer {st.session_state.access_token}'
        }
        respond = requests.post(
            f'{URL}/ask', 
            json={'document_id': document_id, 'question': question},
            headers=headers
        )
        if respond.status_code == 200:
            return respond.json()
        else:
            return {'error': respond.json().get('detail', 'Unknown error occurred')}
    except Exception as e:
        return {'error': f'Query failed: {str(e)}'}

# --------- Sidebar Controls --------- #
st.sidebar.header('⚙️ Settings')
chunk_slider = st.sidebar.slider(
    'Chunk Size', 
    min_value=500, 
    max_value=3000, 
    value=1000, 
    step=100,
    help='Adjust how big each text chunk should be for processing.'
)

# --------- Main Section --------- #
st.title('📚 PDFs in Database')

# Get PDFs
pdfs = get_pdfs()

# Map PDFs
pdf_map = {}
pdf_names = ['Select a PDF...']
if pdfs and isinstance(pdfs, list):
    for pdf in pdfs:
        pdf_name = pdf.get('name', '')
        pdf_id = pdf.get('id')
        if pdf_name and pdf_id is not None:
            display_name = pdf_name.removeprefix(f'{pdf_id}_').removesuffix('.pdf').title()
            pdf_map[display_name] = pdf_id
            pdf_names.append(display_name)
else:
    st.info('No PDFs found. Upload one to get started.')

# Upload new PDF
st.subheader('⬆️ Upload a new PDF')
upload_file = st.file_uploader('Upload PDF:', type=['pdf'])

if upload_file is not None:
    with st.spinner('📤 Uploading PDF...'):
        result = upload_pdf(upload_file, chunk_slider)
    if 'id' in result:
        st.success('✅ PDF uploaded successfully!')
        get_pdfs.clear()
        st.rerun()
    else:
        error_detail = result.get('detail', 'Unknown error')
        if 'already uploaded' in error_detail.lower():
            st.warning('⚠️ This file is already in the database.')
        
st.markdown('---')

# PDF selection
st.subheader('📑 Select an existing PDF')
pdf_option = st.selectbox('Choose a PDF:', options=pdf_names, index=0)

# If PDF selected
if pdf_option and pdf_option != 'Select a PDF...':
    selected_pdf_id = pdf_map.get(pdf_option)

    if selected_pdf_id:
        question_box = st.text_input(
            'Type your question:', 
            placeholder=f'e.g. What is the main idea of {pdf_option}?',
            key='question_input'
        )

        if st.button('Submit Question', key='submit_question'):
            if question_box:
                with st.spinner('🔎 Finding answer...'):
                    answer = ask_query(selected_pdf_id, question_box)
                if 'answer' in answer:
                    st.success('✅ Answer found:')
                    st.write(answer['answer'])
                elif 'error' in answer:
                    st.error(f'Error: {answer['error']}')
                else:
                    st.warning('No answer found. Try another question.')

        # Sidebar delete
        st.sidebar.markdown('---')
        st.sidebar.subheader('Document Actions')
        if st.sidebar.button(f'Delete', type='secondary', key=f'delete_{selected_pdf_id}'):
            with st.spinner('🗑️ Deleting PDF...'):
                response = delete_pdf(selected_pdf_id)
            if response is None:
                # Error already displayed by delete_pdf function
                st.stop()
            elif response.status_code == 204:
                st.success('PDF deleted successfully!')
                get_pdfs.clear()
                st.rerun()
            else:
                # Handle specific error responses
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f'Failed to delete PDF: {error_detail}')
                except:
                    st.error(f'Failed to delete PDF. Status code: {response.status_code}')
