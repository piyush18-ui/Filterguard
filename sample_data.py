"""
Bundled sample messages for demo purposes — one obvious phishing case,
one legitimate-but-urgent case, and one ambiguous case. Use these in
your hackathon pitch to show the tool handling all three situations.
"""

SAMPLE_MESSAGES = [
    {
        "label": "Obvious phishing",
        "subject": "URGENT: Account Suspension Notice",
        "sender_email": "security@sbi-verify-secure.info",
        "body": (
            "Dear Customer, we have detected unauthorized access to your account. "
            "Your account will be suspended within 24 hours unless you verify your "
            "identity immediately. Click here to verify: http://sbi-verify-secure.info/login "
            "Please provide your account password and OTP to confirm your identity."
        ),
        "attachment_filename": None,
    },
    {
        "label": "Legitimate but urgent",
        "subject": "Please review the Q3 report by EOD",
        "sender_email": "priya.sharma@acmecorp.com",
        "body": (
            "Hi team, I need everyone to review the attached Q3 report and send "
            "feedback by end of day today — the board meeting got moved up. "
            "Thanks for the quick turnaround."
        ),
        "attachment_filename": "Q3_report.pdf",
    },
    {
        "label": "Ambiguous case",
        "subject": "Your recent order",
        "sender_email": "support@amazon-help-center.com",
        "body": (
            "Hello, there was an issue processing your recent order. "
            "Please confirm your shipping details by visiting our order page. "
            "If you did not place this order, no action is needed."
        ),
        "attachment_filename": None,
    },
]
