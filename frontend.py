import streamlit as st
import requests

# =========================
# CONFIG
# =========================
BACKEND_URL = "http://localhost:8000/ask"

# =========================
# PAGE SETTINGS
# =========================
st.set_page_config(
    page_title="Mindora AI Therapist",
    page_icon="🧠",
    layout="wide"
)

# =========================
# HEADER
# =========================
st.title("🧠 Mindora – AI Mental Health Therapist")

st.sidebar.header("About")
st.sidebar.info(
    """
    Mindora is an AI-powered mental health support assistant.

    ⚠️ This application is NOT a substitute for licensed
    mental health professionals, emergency services,
    or medical advice.
    """
)

# =========================
# SESSION STATE
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# DISPLAY OLD CHAT
# =========================
for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# CHAT INPUT
# =========================
user_input = st.chat_input(
    "What's on your mind today?"
)

# =========================
# PROCESS USER MESSAGE
# =========================
if user_input:

    # Show user message immediately
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant Response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    BACKEND_URL,
                    json={
                        "message": user_input
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    data = response.json()

                    assistant_reply = data.get(
                        "response",
                        "No response generated."
                    )
                    
                    # Remove WITH TOOL: [...] text from response
                    import re
                    assistant_reply = re.sub(
                        r'\s*WITH TOOL:\s*\[.*?\]',
                        '',
                        assistant_reply,
                        flags=re.IGNORECASE
                    )

                else:

                    assistant_reply = (
                        f"Backend returned status code "
                        f"{response.status_code}"
                    )

            except requests.exceptions.ConnectionError:

                assistant_reply = (
                    "❌ Could not connect to backend.\n\n"
                    "Make sure FastAPI is running:\n\n"
                    "uv run backend/main.py"
                )

            except requests.exceptions.Timeout:

                assistant_reply = (
                    "⏳ Request timed out.\n\n"
                    "The model may still be loading."
                )

            except Exception as e:

                assistant_reply = (
                    f"Unexpected error:\n\n{str(e)}"
                )

        st.markdown(assistant_reply)

    # Save assistant message
    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": assistant_reply
        }
    )

# =========================
# CLEAR CHAT BUTTON
# =========================
st.sidebar.divider()

if st.sidebar.button("🗑️ Clear Chat"):

    st.session_state.chat_history = []

    st.rerun()