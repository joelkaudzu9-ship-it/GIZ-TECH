# app/utils/notifications.py
from app.models import Business, Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class NotificationService:
    @staticmethod
    def send_email_notification(message):
        """Send email notification for new message"""
        business = Business.query.first()

        if not business or not business.email_notifications:
            return False

        try:
            # Email configuration - add these to your .env file
            smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('MAIL_PORT', 587))
            smtp_username = os.getenv('MAIL_USERNAME')
            smtp_password = os.getenv('MAIL_PASSWORD')

            if not smtp_username or not smtp_password:
                print("Email not configured - skipping notification")
                return False

            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = business.email
            msg['Subject'] = f"New Message about {message.product.title}"

            body = f"""
            <h2>New Customer Inquiry</h2>
            <p><strong>Product:</strong> {message.product.title}</p>
            <p><strong>From:</strong> {message.name} ({message.email})</p>
            <p><strong>Message:</strong></p>
            <p>{message.message}</p>
            <hr>
            <p><a href="http://localhost:5000/dashboard/messages">View in Dashboard</a></p>
            """

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()

            print(f"✅ Email notification sent to {business.email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

    @staticmethod
    def send_whatsapp_notification(message):
        """Send WhatsApp notification for new message"""
        business = Business.query.first()

        if not business or not business.whatsapp_notifications:
            return False

        try:
            # You'll need WhatsApp Business API credentials
            # This is a placeholder - implement with your WhatsApp provider
            whatsapp_api_key = os.getenv('WHATSAPP_API_KEY')

            if not whatsapp_api_key:
                print("WhatsApp not configured - skipping notification")
                return False

            # Example using WhatsApp Business API
            # Implement based on your WhatsApp provider

            print(f"📱 WhatsApp notification would be sent to {business.whatsapp}")
            return True

        except Exception as e:
            print(f"❌ Failed to send WhatsApp: {e}")
            return False

    @staticmethod
    def send_daily_digest():
        """Send daily digest of activity"""
        from datetime import datetime, timedelta
        from app.models import Product, Message

        business = Business.query.first()

        if not business or not business.daily_digest:
            return False

        yesterday = datetime.utcnow() - timedelta(days=1)

        # Get yesterday's activity
        new_messages = Message.query.filter(Message.created_at >= yesterday).count()
        new_views = db.session.query(db.func.sum(Product.views)).filter(Product.last_viewed >= yesterday).scalar() or 0

        # Send email digest
        try:
            msg = MIMEMultipart()
            msg['From'] = os.getenv('MAIL_USERNAME')
            msg['To'] = business.email
            msg['Subject'] = f"Your Daily Digest - {datetime.utcnow().strftime('%Y-%m-%d')}"

            body = f"""
            <h2>Daily Activity Report</h2>
            <p><strong>Date:</strong> {yesterday.strftime('%Y-%m-%d')}</p>
            <hr>
            <p><strong>New Messages:</strong> {new_messages}</p>
            <p><strong>New Views:</strong> {new_views}</p>
            <hr>
            <p><a href="http://localhost:5000/dashboard">View Dashboard</a></p>
            """

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(os.getenv('MAIL_SERVER'), int(os.getenv('MAIL_PORT')))
            server.starttls()
            server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
            server.send_message(msg)
            server.quit()

            print(f"✅ Daily digest sent to {business.email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send digest: {e}")
            return False