import streamlit as st
from llm_chains import load_normal_chain, load_pdf_chat_chain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from streamlit_mic_recorder import mic_recorder
from utils import save_chat_history_json, get_timestamp, load_chat_history_json
from image_handler import handle_image
from audio_handler import transcribe_audio
from pdf_handler import add_documents_to_db
from html_templates import get_bot_template, get_user_template, css
from io import BytesIO
import yaml
import os

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def load_chain(chat_history):
    if st.session_state.pdf_chat:
        return load_pdf_chat_chain(chat_history)
    return load_normal_chain(chat_history)

def clear_chat_history():
    st.session_state.history.clear()
    if st.session_state.session_key != "new_session":
        chat_file = config["chat_history_path"] + st.session_state.session_key
        if os.path.exists(chat_file):
            os.remove(chat_file)
    st.session_state.last_processed = None
    st.session_state.pending_transcription = ""
    st.rerun()

def main():
    st.title("N.O.R.A")
    st.subheader("Your AI Medical Assistant")
    st.write(css, unsafe_allow_html=True)
    
    # Initialize session state
    if "history" not in st.session_state:
        st.session_state.history = StreamlitChatMessageHistory(key="chat_history")
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "pending_transcription" not in st.session_state:
        st.session_state.pending_transcription = ""
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "last_processed" not in st.session_state:
        st.session_state.last_processed = None
    if "session_key" not in st.session_state:
        st.session_state.session_key = "new_session"
    if "pdf_chat" not in st.session_state:
        st.session_state.pdf_chat = False

    # Sidebar controls
    st.sidebar.title("Chat Settings")
    if st.sidebar.button("🧹 Clear Chat History"):
        clear_chat_history()
    
    chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])
    session_index = chat_sessions.index(st.session_state.session_key)
    st.sidebar.selectbox("Select chat session", chat_sessions, key="session_key", index=session_index)
    st.sidebar.toggle("📄 PDF Chat Mode", key="pdf_chat")

    # Load chat history
    if st.session_state.session_key != "new_session":
        loaded_history = load_chat_history_json(config["chat_history_path"] + st.session_state.session_key)
        st.session_state.history.clear()
        for msg in loaded_history:
            if msg["type"] == "human":
                st.session_state.history.add_user_message(msg["content"])
            else:
                st.session_state.history.add_ai_message(msg["content"])

    # Display chat history
    for message in st.session_state.history.messages:
        cleaned_content = message.content.replace("<s>", "").replace("</s>", "")
        if message.type == "ai":
            st.write(get_bot_template(cleaned_content), unsafe_allow_html=True)
        else:
            st.write(get_user_template(cleaned_content), unsafe_allow_html=True)

    # Chat input section
    with st.form("chat_input", clear_on_submit=True):
        user_input = st.text_input(
            "Type your message here",
            key="user_input",
            value=st.session_state.pending_transcription or "",
            help="Your voice transcription will appear here"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            voice_recording = mic_recorder(
                start_prompt="🎤 Record",
                stop_prompt="⏹ Stop",
                just_once=True,
                key="mic_recorder"
            )
        with col2:
            submitted = st.form_submit_button("💬 Send")
        
        if submitted and user_input:
            if user_input != st.session_state.last_processed:
                st.session_state.processing = True
                st.session_state.last_processed = user_input
                st.rerun()

    # Audio handling
    if voice_recording and voice_recording.get("bytes"):
        with st.spinner("Transcribing..."):
            try:
                transcribed = transcribe_audio(voice_recording["bytes"])
                if transcribed:
                    st.session_state.pending_transcription = transcribed
                    st.rerun()
                else:
                    st.error("Failed to transcribe audio")
            except Exception as e:
                st.error(f"Transcription error: {str(e)}")
                st.session_state.pending_transcription = ""

    # Process user input
    if st.session_state.processing and st.session_state.last_processed:
        with st.spinner("Generating response..."):
            try:
                llm_chain = load_chain(st.session_state.history)
                response = llm_chain.run(st.session_state.last_processed)
                
                if not response.strip():
                    response = "I couldn't process that request. Please try rephrasing."
                
                # Add to chat history
                current_messages = st.session_state.history.messages
                if not current_messages or current_messages[-1].content != response:
                    st.session_state.history.add_user_message(st.session_state.last_processed)
                    st.session_state.history.add_ai_message(response)
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                response = "An error occurred while processing your request."
                
            finally:
                st.session_state.processing = False
                st.session_state.pending_transcription = ""
                st.session_state.last_processed = None
                st.rerun()

    # File upload handlers
    st.sidebar.header("File Uploads")
    uploaded_audio = st.sidebar.file_uploader("🎵 Upload audio", type=["wav", "mp3", "ogg"])
    uploaded_image = st.sidebar.file_uploader("🖼️ Upload image", type=["jpg", "jpeg", "png"])
    uploaded_pdf = st.sidebar.file_uploader("📄 Upload PDF", type=["pdf"], accept_multiple_files=True)

    if uploaded_pdf:
        with st.spinner("Processing PDFs..."):
            add_documents_to_db(uploaded_pdf)
            st.rerun()

    if uploaded_audio:
        with st.spinner("Transcribing audio..."):
            try:
                transcribed = transcribe_audio(uploaded_audio.getvalue())
                if transcribed:
                    st.session_state.pending_transcription = transcribed
                    st.rerun()
                else:
                    st.error("Failed to transcribe uploaded audio")
            except Exception as e:
                st.error(f"Audio error: {str(e)}")

    if uploaded_image and st.session_state.last_processed:
        with st.spinner("Processing image..."):
            try:
                response = handle_image(uploaded_image.getvalue(), st.session_state.last_processed)
                st.session_state.history.add_user_message(st.session_state.last_processed)
                st.session_state.history.add_ai_message(response)
                st.session_state.last_processed = None
                st.rerun()
            except Exception as e:
                st.error(f"Image processing error: {str(e)}")

    # Save chat history
    if st.session_state.session_key != "new_session":
        save_chat_history_json(
            [{"type": "human" if msg.type == "human" else "ai", "content": msg.content} 
             for msg in st.session_state.history.messages],
            config["chat_history_path"] + st.session_state.session_key
        )

if __name__ == "__main__":
    main()