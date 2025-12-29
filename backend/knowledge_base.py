# Tiny demo KB (replace with the client's FAQs later)

KB = {
    "login_issue": {
        "title": "Login Troubleshooting",
        "steps": [
            "Confirm you’re using the correct email address.",
            "Try the 'Forgot password' flow and reset your password.",
            "Clear browser cache/cookies or try an incognito window.",
            "Try a different browser/device to rule out extensions.",
            "If you use SSO, confirm your identity provider is working."
        ],
        "followup": "If you tell me what error you see (or paste it), I can narrow it down."
    },
    "billing": {
        "title": "Billing & Payments",
        "steps": [
            "Invoices are typically available in your account billing settings.",
            "Check if your payment method is expired or needs re-verification.",
            "If you see duplicate charges, share the invoice IDs so we can investigate."
        ],
        "followup": "Are you asking about an invoice, a failed payment, or an unexpected charge?"
    },
    "refund": {
        "title": "Refunds",
        "steps": [
            "Please share the order/invoice ID and the reason for the refund request.",
            "If the charge is recent, it may still be pending and can drop off automatically.",
            "We can escalate to a human agent for account-specific checks."
        ],
        "followup": "Please share the invoice/order ID (or last 4 digits + date), and I’ll help."
    },
    "technical_issue": {
        "title": "Technical Troubleshooting",
        "steps": [
            "Confirm the issue happens on multiple devices/browsers.",
            "Check your network/VPN settings and retry.",
            "If possible, provide screenshots or error logs.",
            "Share steps to reproduce: what you clicked + what you expected + what happened."
        ],
        "followup": "What were you doing right before the issue happened?"
    },
    "product_question": {
        "title": "Product Information",
        "steps": [
            "Tell me which feature you’re looking for and your goal.",
            "I can suggest the best workflow and recommended setup."
        ],
        "followup": "What outcome are you trying to achieve with the product?"
    },
    "general": {
        "title": "General Help",
        "steps": [
            "Tell me what you’re trying to do and where you’re stuck.",
            "If it’s urgent, I can escalate to a human agent."
        ],
        "followup": "What’s the main issue: login, billing, technical, or something else?"
    }
}

def kb_answer(intent: str) -> str:
    data = KB.get(intent) or KB["general"]
    steps = "\n".join([f"- {s}" for s in data["steps"]])
    return f"**{data['title']}**\n\n{steps}\n\n{data['followup']}"
