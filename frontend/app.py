import streamlit as st
import websocket
import json

st.set_page_config(page_title="WebSocket Chatbot Demo", layout="centered")
st.title("Real-time Support Chatbot")

WS_URL = "ws://localhost:8000/ws/chat"

# -------------------------
# Session state
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 **Hey! Welcome to Customer Support.**\n\nHow can I help you today?"
        }
    ]

# -------------------------
# Render chat history
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# User input
# -------------------------
user_input = st.chat_input("Type your message")

if user_input:
    # Show user message immediately
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # -------------------------
    # WebSocket: open → send → receive → close
    # -------------------------
    ws = websocket.create_connection(WS_URL)

    ws.send(json.dumps({
        "message": user_input
    }))

    response = ws.recv()
    ws.close()

    data = json.loads(response)
    reply = data["reply"]

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    with st.chat_message("assistant"):
        st.markdown(reply)
