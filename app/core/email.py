import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logger import logger
from app.models.order import Order

def send_real_email(recipient_email: str, subject: str, html_content: str) -> None:
    """
    Sends an email using SMTP configuration.
    Runs inside FastAPI's BackgroundTasks to prevent blocking the main event loop.
    """
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        logger.warning("SMTP settings are incomplete. Skipping email delivery.")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = recipient_email

    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, recipient_email, message.as_string())
        logger.info(f"Email successfully sent to {recipient_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email} due to error: {e}")


def generate_receipt_email_content(order: Order, payment_id: str) -> str:
    """
    Generates an HTML receipt/ticket breakdown for a paid Order.
    """
    items_html = ""
    for item in order.items:
        item_subtotal = item.quantity * item.unit_price
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item.product_name}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{item.quantity}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${item.unit_price:.2f}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${item_subtotal:.2f}</td>
        </tr>
        """

    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; padding: 20px; border-radius: 8px;">
                <h2 style="color: #2c3e50; text-align: center;">🍔 FastTable Restaurant</h2>
                <h3 style="text-align: center; color: #27ae60;">Payment Receipt Confirmed</h3>
                <hr style="border: 0; border-top: 1px solid #eee;">
                
                <p><strong>Table Number:</strong> #{order.table_number}</p>
                <p><strong>Order ID:</strong> {order.id}</p>
                <p><strong>Transaction Ref:</strong> {payment_id}</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Item</th>
                            <th style="padding: 8px; text-align: center; border-bottom: 2px solid #ddd;">Qty</th>
                            <th style="padding: 8px; text-align: right; border-bottom: 2px solid #ddd;">Unit Price</th>
                            <th style="padding: 8px; text-align: right; border-bottom: 2px solid #ddd;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <div style="text-align: right; margin-top: 20px;">
                    <h3 style="color: #2c3e50;">Total Paid: ${order.total_amount:.2f} USD</h3>
                </div>
                
                <hr style="border: 0; border-top: 1px solid #eee; margin-top: 20px;">
                <p style="text-align: center; font-size: 12px; color: #7f8c8d;">
                    Thank you for dining with us! If you have any questions, please contact our support staff.
                </p>
            </div>
        </body>
    </html>
    """
