import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.router import handle_message


app = FastAPI()

@app.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket):
    await websocket.accept()
    session_state = {
        "messages": [],
        "awaiting_email": False,
        "ticket": None
    }

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            user_message = payload.get("message", "")

            # Store user message
            session_state["messages"].append({
                "role": "user",
                "content": user_message
            })

            # Process
            result = handle_message(user_message, session_state)

            reply = result["reply"]

            # Store assistant message
            session_state["messages"].append({
                "role": "assistant",
                "content": reply
            })

            await websocket.send_text(json.dumps({
                "reply": reply,
                "intent": result.get("intent"),
                "ticket": result.get("ticket")
            }))

    except WebSocketDisconnect:
        print("Client disconnected")
