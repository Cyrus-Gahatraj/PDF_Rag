import streamlit as st
import requests

URL = 'http://localhost:8000'

if "access_token" not in st.session_state or not st.session_state.get("logged_in"):
    st.warning("Please login first!")
    st.stop()

headers = {
    "Authorization": f"Bearer {st.session_state.access_token}"
}

st.markdown("""
<style>
.stFileUploader p {
    font-size: 38px;
    font-weight: 700;
}
            
.indented-text {
    padding-left: 50px; 
    font-size: 32px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_pdfs():
    try:
        with st.spinner('Please wait while fetching the data...', show_time=True):
            respond = requests.get(f'{URL}/documents', headers=headers)
        if respond.status_code == 200:
            return respond.json()
        else:
            st.error(f"Failed to fetch PDFs: {respond.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching PDFs: {str(e)}")
        return []

def upload_pdf(pdf_file, chunk_size=1000):
    try:
        file = {
            'file': (pdf_file.name, pdf_file.getvalue(), pdf_file.type)
        }
        data = {
            'chunk_size': chunk_size
        }
        respond = requests.post(
            f'{URL}/documents/upload',
            files=file,
            data=data,
            headers=headers
        )
        return respond.json()
    except Exception as e:
        return {"detail": f"Upload failed: {str(e)}"}

def delete_pdf(pdf_id):
    try:
        respond = requests.delete(f'{URL}/documents/{pdf_id}', headers=headers)
        return respond
    except Exception as e:
        st.error(f"Delete failed: {str(e)}")
        return None

def ask_query(document_id: int, question: str):
    try:
        respond = requests.post(
            f'{URL}/ask', 
            json={
                'document_id': document_id,
                'question': question, 
            },
            headers=headers
        )
        if respond.status_code == 200:
            return respond.json()
        else:
            return {"error": respond.json().get('detail', 'Unknown error occurred')}
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}

# Main application
st.header('PDFs in Database 📚')

# Get PDFs with error handling
pdfs = get_pdfs()

# Safely create PDF map with proper error handling
pdf_map = {}
pdf_names = ["Select a PDF..."]

if pdfs and isinstance(pdfs, list):
    for pdf in pdfs:
        # Safely get name and id with defaults
        pdf_name = pdf.get('name', '')
        pdf_id = pdf.get('id')
        
        # Only add if we have both name and id
        if pdf_name and pdf_id is not None:
            # Clean up the name for display
            display_name = pdf_name.removesuffix('.pdf').title() if pdf_name else 'Unknown PDF'
            pdf_map[display_name] = pdf_id
            pdf_names.append(display_name)
else:
    st.info("No PDFs found in database. Upload a PDF to get started.")

# File uploader
upload_file = st.file_uploader("Upload More:", type=["pdf"])

# PDF selection
if pdf_names:
    pdf_option = st.selectbox(
        label='Select a PDF:', 
        options=pdf_names, 
        index=0
    )
else:
    pdf_option = None
    st.info("No PDFs available. Please upload a PDF first.")

# Handle PDF operations if a PDF is selected
if pdf_option and pdf_option != "Select a PDF...":
    selected_pdf_id = pdf_map.get(pdf_option)
    
    if selected_pdf_id:
        # Question input
        question_box = st.text_input(
            f'Ask a question about {pdf_option}:',
            placeholder=f"Type your question about {pdf_option}...",
            key="question_input"
        )
        
        submit_button = st.button('Submit', key="submit_question")
        
        # Handle question submission
        if submit_button and question_box:
            with st.spinner('Searching for answer...'):
                answer = ask_query(selected_pdf_id, question_box)
            
            if 'answer' in answer:
                st.success("Answer:")
                st.write(answer['answer'])
            elif 'error' in answer:
                st.error(f"Error: {answer['error']}")
            else:
                st.warning("No answer found. Please try a different question.")
        
        # Delete button in sidebar
        with st.sidebar:
            st.subheader("Document Actions")
            delete_button = st.button(
                'Delete PDF', 
                key="delete_pdf",
                type="secondary"
            )
            
            if delete_button:
                if st.confirm(f"Are you sure you want to delete '{pdf_option}'? This action cannot be undone."):
                    response = delete_pdf(selected_pdf_id)
                    if response and response.status_code == 200:
                        st.success('PDF deleted successfully!')
                        get_pdfs.clear()
                        st.rerun()
                    else:
                        st.error('Failed to delete PDF. Please try again.')
    else:
        st.error("Invalid PDF selection. Please try again.")

# Handle file upload
if upload_file is not None:
    with st.spinner('Uploading PDF...'):
        result = upload_pdf(upload_file)
    
    if 'id' in result:
        st.success("✅ PDF uploaded successfully! Refresh the page to see the new document")
        get_pdfs.clear()
        # Optional: auto-refresh after a short delay
        st.rerun()
    else:
        error_detail = result.get("detail", "Unknown error")
        if "already uploaded" in error_detail.lower():
            st.warning("⚠️ This file is already in the database.")
        else:
            st.error(f"❌ Upload failed: {error_detail}")

# Display empty state if no PDFs
if not pdfs or len(pdf_names) <= 1:
    st.markdown("---")
    st.info("👆 Upload a PDF above to start chatting with your documents!")