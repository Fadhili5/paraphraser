import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY

class EmailService:
    @staticmethod
    async def send_password_email(email: str, reset_link: str):
        if not settings.RESEND_API_KEY:
            raise RuntimeError(
                "RESEND_API_KEY is not configured"
            )
        resend.api_key = settings.RESEND_API_KEY

        resend.Emails.send({
            "from": "noreply@paraphraser.com",
            "to": email,
            "subject": "Reset Password Email",
            "html": f"""
                <h2>Password Reset</h2>
                
                <p>
                    Click on the link below to reset your password
                </p>

                <a href="{reset_link}">
                    Reset Password
                </a>"""
        })