import streamlit as st
import requests

# URL to your FastAPI backend
BACKEND_URL= "http://localhost:3030"


# Chatbot section
st.set_page_config(page_title="Multi Agent Assistant", page_icon="🧠")
st.title("Multi Agent Assistant")

with st.sidebar:
    # File upload section
    if "file_names" not in st.session_state:
        st.session_state.file_names = []

    uploaded_files = st.file_uploader("Choose a file to upload", type=["pdf"], accept_multiple_files=True)
    if st.button("🚀 Upload to Backend"):
        for uploaded_file in uploaded_files: 
            st.success(f"File selected: {uploaded_file.name}")
            if uploaded_file:
                    try:
                        # Send file to FastAPI
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        res = requests.post(f"{BACKEND_URL}/upload_file", files=files)

                        if res.status_code == 200: 
                            response = res.json()
                            st.success(f"{response['message']}")
                            st.session_state.file_names.append(response["filename"])
                        else:
                            st.error(f"Upload failed with status code {res.status_code}")

                    except Exception as e:
                        st.error(f"Error: {e}") 
                        
    # delete uploaded files                    
    if st.button("Clear Uploaded Files"):
        res = requests.delete(f"{BACKEND_URL}/clear_uploaded_files")
        if res.status_code == 200:
            st.success(res.json()["message"])
            st.session_state.file_names = []  # clear frontend file list too
        else:
            st.error("Could not clear files.")
                        

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your research question..."):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Build full conversation history (excluding current prompt)
    full_prompt = "\n".join(
        [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages]
    )

    payload = {"query": full_prompt,
               }
    # Show assistant message streaming
    with st.chat_message("assistant"):
        output_box = st.empty()
        streamed_reply = ""

        try:
            # Send request with stream=True
            with requests.post(
                f"{BACKEND_URL}/conversation",
                json=payload,
                stream=True,
            ) as res:
                res.raise_for_status()

                for chunk in res.iter_content(chunk_size=1):
                    if chunk:
                        streamed_reply += chunk.decode("utf-8", errors="ignore") # Handle decoding errors
                        output_box.markdown(streamed_reply)
                st.session_state.file_names = [] # clear frontend file list too

        except Exception as e:
            streamed_reply = f"Error: {e}"
            output_box.markdown(streamed_reply)
    # Save assistant message to history
    st.session_state.messages.append(
        {"role": "assistant", "content": streamed_reply}
    )


