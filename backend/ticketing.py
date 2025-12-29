import time
import uuid

def create_ticket(conversation, user_email=None):
    """
    Demo ticket creation.
    Replace with Zendesk/Freshdesk/HubSpot/Jira/Email integration later.
    """
    ticket_id = f"TCK-{uuid.uuid4().hex[:8].upper()}"
    created_at = time.strftime("%Y-%m-%d %H:%M:%S")

    # In a real system, you'd store to DB or send to helpdesk API.
    ticket = {
        "ticket_id": ticket_id,
        "created_at": created_at,
        "user_email": user_email,
        "summary": (conversation[-1]["content"][:120] if conversation else "Support request"),
        "transcript": conversation,
        "status": "open"
    }
    return ticket
