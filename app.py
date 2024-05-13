import streamlit as st
from PIL import Image
import requests
import uuid
from decouple import config
import io

API_URL = config("https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyDK2coCja1cwO1Ub28Q1a8fJ6v5FQYbseI")

st.sidebar.title("Google's Gemini")
system_prompt = st.sidebar.text_area("System Prompt:", value="You are a helpful AI Assistant.")
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def chatbot(session_id):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message['content'])

    prompt = st.chat_input("Message Gemini...")

    if not prompt:
        st.markdown(
        """
        <h1 style='font-size: 36px;'>
            👋 Welcome to Google's Gemini Model 🤖
        </h1>
        """,
        unsafe_allow_html=True
        )
        st.markdown("Things you can do with this bot:\n\n1. Converse with chatbot\n2. Ask questions on images\n3. Ask questions on PDFs")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            data = {'session_id': st.session_state.session_id, 'system_prompt': system_prompt, 'prompt': prompt}
            response = requests.post(f"{API_URL}/chat/", data=data)
            result = response.json()
            result = result['generated_text']

        with st.chat_message("assistant"):
            st.markdown(result)

        st.session_state.messages.append({"role": "assistant", "content": result})

def imagebot(session_id):
    uploaded_file = st.file_uploader("Please upload an image", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Your uploaded image', width=200)
        prompt = st.text_input(label="Ask about uploaded image...", key=session_id)
        if prompt is not None and st.button("Ask"):
            with st.spinner("Thinking..."):
                data = {'session_id': session_id,
                        'system_prompt': system_prompt,
                        'prompt': prompt,
                        }
                files = {'image': uploaded_file.getvalue()}
                response = requests.post(f"{API_URL}/image/", data=data, files=files)

            if response.status_code == 200:
                result = response.json()
                result = result['generated_text']
                st.markdown(result)
            else:
                st.error("Failed to send the data.")

def pdfchat(session_id):
    uploaded_pdf = st.file_uploader("Please upload a PDF", type=["pdf"])
    if uploaded_pdf is not None:
        pdf_bytes = uploaded_pdf.read()
        st.success("PDF Uploaded Succesfully!")
        prompt = st.text_input(label="Ask about uploaded PDF...", key=session_id)
        if prompt is not None and st.button("Ask"):
            with st.spinner("Thinking..."):
                files = {"pdf": (uploaded_pdf.name, pdf_bytes, "application/pdf")}
                data = {"session_id": session_id, "prompt": prompt}
                response = requests.post(f"{API_URL}/pdf/", data=data, files=files)

            if response.status_code == 200:
                result = response.json()
                result = result['generated_text']
                st.markdown(result)
            else:
                st.error("Failed to send the data.")



def chat():
    chatbot(st.session_state.session_id)

def image():
    imagebot(st.session_state.session_id)

def pdf():
    pdfchat(st.session_state.session_id)

PAGES = {
    "Converse with Chatbot": chat,
    "Image-Bot": image,
    "Chat with PDF": pdf,
}

selection = st.sidebar.radio("", list(PAGES.keys()))
page = PAGES[selection]
page()
