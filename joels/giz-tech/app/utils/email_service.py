# app/utils/email_service.py
from app.models import Subscriber, Product
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from flask import url_for  # Add this import


class EmailService:
    @staticmethod
    def send_product_notification(product, action='new'):
        """Send notification to all subscribers about product update"""
        subscribers = Subscriber.query.filter_by(is_active=True).all()

        if not subscribers:
            return

        subject = f"New Product: {product.title}" if action == 'new' else f"Product Sold: {product.title}"

        for subscriber in subscribers:
            try:
                # Generate URLs using Flask's url_for
                product_url = url_for('main.product_detail', slug=product.slug or product.id, _external=True)
                unsubscribe_url = url_for('main.unsubscribe', email=subscriber.email, _external=True)
                products_url = url_for('main.products', _external=True)

                msg = MIMEMultipart()
                msg['From'] = os.getenv('MAIL_USERNAME', 'noreply@giztech.com')
                msg['To'] = subscriber.email
                msg['Subject'] = subject

                if action == 'new':
                    body = f"""
                    <h2>New Product Added!</h2>
                    <h3>{product.title}</h3>
                    <p><strong>Price:</strong> MWK {product.price:,.0f}</p>
                    <p><strong>Description:</strong> {product.description[:200]}...</p>
                    <p><a href="{product_url}">View Product</a></p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        <a href="{unsubscribe_url}">Unsubscribe</a>
                    </p>
                    """
                else:
                    body = f"""
                    <h2>Product Sold Out!</h2>
                    <h3>{product.title}</h3>
                    <p>This popular item has been sold. Check out our other products!</p>
                    <p><a href="{products_url}">Browse More Products</a></p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        <a href="{unsubscribe_url}">Unsubscribe</a>
                    </p>
                    """

                msg.attach(MIMEText(body, 'html'))

                # Send email (configure with your SMTP settings)
                if os.getenv('MAIL_USERNAME') and os.getenv('MAIL_PASSWORD'):
                    server = smtplib.SMTP(os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
                                          int(os.getenv('MAIL_PORT', 587)))
                    server.starttls()
                    server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
                    server.send_message(msg)
                    server.quit()

                print(f"📧 Notification sent to {subscriber.email}")

            except Exception as e:
                print(f"❌ Failed to send email to {subscriber.email}: {e}")