import json
import re
from typing import Dict, List, Tuple
from backend.prompts import SYSTEM_INSTRUCTIONS, INTENT_PROMPT
from backend.knowledge_base import kb_answer
from backend.gemini_client import generate_text
from backend.ticketing import create_ticket

INTENTS = {
    "login_issue", "billing", "product_question", "refund", "technical_issue", "human", "general"
}

EMAIL_REGEX = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

def _safe_json_extract(text: str) -> Dict:
    """
    Extract JSON from Gemini output. If it returns extra text, try to recover.
    """
    text = text.strip()
    # If it's already JSON:
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    # Try to find first JSON object in text
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if m:
        return json.loads(m.group(0))

    raise ValueError("No JSON found in model output")

def detect_intent_llm(user_message: str) -> Tuple[str, float, str]:
    prompt = INTENT_PROMPT.replace("{{USER_MESSAGE}}", user_message)
    raw = generate_text(system_instructions="You are a strict JSON generator.", user_content=prompt, temperature=0.0)

    try:
        data = _safe_json_extract(raw)
        intent = data.get("intent", "general")
        conf = float(data.get("confidence", 0.5))
        reason = str(data.get("reason", ""))
        if intent not in INTENTS:
            return "general", 0.3, "Unknown intent from model; defaulted to general."
        return intent, max(0.0, min(1.0, conf)), reason
    except Exception:
        # Fallback heuristic if JSON parsing fails
        t = user_message.lower()
        if any(w in t for w in ["password", "login", "log in", "sign in", "otp"]):
            return "login_issue", 0.6, "Heuristic fallback"
        if any(w in t for w in ["invoice", "billing", "charged", "payment", "card"]):
            return "billing", 0.6, "Heuristic fallback"
        if any(w in t for w in ["refund", "cancel", "chargeback"]):
            return "refund", 0.6, "Heuristic fallback"
        if any(w in t for w in ["bug", "error", "not working", "crash", "issue"]):
            return "technical_issue", 0.6, "Heuristic fallback"
        if any(w in t for w in ["human", "agent", "representative", "call me"]):
            return "human", 0.7, "Heuristic fallback"
        return "general", 0.4, "Heuristic fallback"

def build_llm_support_reply(user_message: str, intent: str, kb_text: str, history: List[Dict]) -> str:
    """
    Produce a nice customer-support response grounded on KB (for the POC).
    """
    # Keep history short for demo
    last_turns = history[-6:] if history else []
    history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in last_turns])

    user_content = f"""
Conversation (recent):
{history_text}

User message:
{user_message}

Detected intent: {intent}

Knowledge Base (use this if relevant; do not invent facts beyond it):
{kb_text}

Write a helpful support response.
- Prefer step-by-step.
- Ask a clarifying question if needed.
- If user seems frustrated or requests escalation, propose human handoff.
"""

    reply = generate_text(system_instructions=SYSTEM_INSTRUCTIONS, user_content=user_content, temperature=0.3).strip()
    if not reply:
        # Fallback to KB-only response
        reply = kb_text
    return reply

def handle_message(user_message: str, session_state: Dict) -> Dict:
    """
    Main orchestration.
    session_state holds:
      - messages: list of {role, content}
      - awaiting_email: bool
      - ticket: dict (if created)
    """
    messages = session_state.get("messages", [])
    session_state.setdefault("awaiting_email", False)
    session_state.setdefault("ticket", None)

    # If we asked for email earlier (human escalation)
    if session_state["awaiting_email"]:
        if EMAIL_REGEX.search(user_message or ""):
            email = EMAIL_REGEX.search(user_message).group(0)
            ticket = create_ticket(conversation=messages, user_email=email)
            session_state["ticket"] = ticket
            session_state["awaiting_email"] = False
            return {
                "reply": f"✅ Thanks! I’ve logged your request as **{ticket['ticket_id']}**. A human agent will contact you at **{email}**.",
                "intent": "human",
                "ticket": ticket
            }
        else:
            return {
                "reply": "Could you share a valid email address so a human agent can reach you?",
                "intent": "human",
                "ticket": session_state["ticket"]
            }

    intent, conf, reason = detect_intent_llm(user_message)

    # Explicit human request
    if intent == "human" or ("agent" in user_message.lower() and conf >= 0.4):
        session_state["awaiting_email"] = True
        # Create ticket now (without email) so we can show it in UI
        ticket = create_ticket(conversation=messages, user_email=None)
        session_state["ticket"] = ticket
        return {
            "reply": (
                "Sure — I can escalate this.\n\n"
                f"🧾 I created ticket **{ticket['ticket_id']}**.\n\n"
                "What email should the support agent use to contact you?"
            ),
            "intent": "human",
            "ticket": ticket
        }

    kb_text = kb_answer(intent)
    reply = build_llm_support_reply(user_message, intent, kb_text, messages)

    return {
        "reply": reply,
        "intent": intent,
        "meta": {"confidence": conf, "reason": reason},
        "ticket": session_state["ticket"]
    }
