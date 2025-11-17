"""
Email service for sending order confirmation and notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        self.mail_port = int(os.getenv('MAIL_PORT', 587))
        self.mail_username = os.getenv('MAIL_USERNAME')
        self.mail_password = os.getenv('MAIL_PASSWORD')
        self.mail_sender = os.getenv('MAIL_DEFAULT_SENDER', 'ShopScale <noreply@shopscale.com>')
    
    def send_order_confirmation(self, customer_email, customer_name, order_id, total_amount, items, payment_method):
        """Send order confirmation email to customer"""
        try:
            if not self.mail_username or not self.mail_password:
                print("Email credentials not configured in .env file")
                print(f"[LOG] Order confirmation would be sent to {customer_email}")
                return True
            
            subject = f"Order Confirmation - Order #{order_id}"
            
            # Create email body
            html_content = self._create_order_email_html(
                customer_name, order_id, total_amount, items, payment_method
            )
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.mail_sender
            msg['To'] = customer_email
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.mail_server, self.mail_port)
            server.starttls()
            server.login(self.mail_username, self.mail_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Order confirmation email sent to {customer_email}")
            return True
        
        except Exception as e:
            print(f"❌ Error sending order confirmation email: {e}")
            # Log error but don't fail the order
            return False
    
    def send_order_shipped(self, customer_email, customer_name, order_id, tracking_number=None):
        """Send order shipped notification email"""
        try:
            if not self.mail_username or not self.mail_password:
                print(f"[LOG] Shipping notification would be sent to {customer_email}")
                return True
            
            subject = f"Your Order #{order_id} Has Shipped!"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">Order Shipped! 🚚</h2>
                        <p>Dear {customer_name},</p>
                        <p>Great news! Your order <strong>#{order_id}</strong> has been shipped.</p>
                        {f'<p>Tracking Number: <strong>{tracking_number}</strong></p>' if tracking_number else ''}
                        <p>You can track your package status in your account or using the tracking number above.</p>
                        <p>Thank you for shopping with ShopScale!</p>
                        <p>Best regards,<br>ShopScale Team</p>
                    </div>
                </body>
            </html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.mail_sender
            msg['To'] = customer_email
            
            msg.attach(MIMEText(html_content, 'html'))
            
            server = smtplib.SMTP(self.mail_server, self.mail_port)
            server.starttls()
            server.login(self.mail_username, self.mail_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Shipped notification email sent to {customer_email}")
            return True
        
        except Exception as e:
            print(f"❌ Error sending shipped notification: {e}")
            return False
    
    def _create_order_email_html(self, customer_name, order_id, total_amount, items, payment_method):
        """Create HTML email content for order confirmation"""
        items_html = ""
        for item in items:
            items_html += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; text-align: left;">{item['product_name']}</td>
                <td style="padding: 10px; text-align: center;">{item['quantity']}</td>
                <td style="padding: 10px; text-align: right;">₹{item['unit_price']:.2f}</td>
                <td style="padding: 10px; text-align: right;">₹{item['total_price']:.2f}</td>
            </tr>
            """
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 8px;">
                    <div style="background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
                        <h1 style="margin: 0;">Order Confirmation</h1>
                        <p style="margin: 5px 0; font-size: 14px;">Order #{order_id}</p>
                    </div>
                    
                    <div style="padding: 20px; background-color: white;">
                        <p>Dear {customer_name},</p>
                        <p>Thank you for your order! We've received your order and it's being prepared for shipment.</p>
                        
                        <h3 style="color: #2c3e50; margin-top: 25px; margin-bottom: 15px;">Order Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background-color: #ecf0f1;">
                                    <th style="padding: 10px; text-align: left;">Product</th>
                                    <th style="padding: 10px; text-align: center;">Qty</th>
                                    <th style="padding: 10px; text-align: right;">Price</th>
                                    <th style="padding: 10px; text-align: right;">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items_html}
                            </tbody>
                        </table>
                        
                        <div style="margin-top: 20px; border-top: 2px solid #ecf0f1; padding-top: 15px;">
                            <table style="width: 100%; text-align: right;">
                                <tr>
                                    <td style="padding: 8px;">Subtotal:</td>
                                    <td style="padding: 8px;"><strong>₹{total_amount * 0.85:.2f}</strong></td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;">Tax (18%):</td>
                                    <td style="padding: 8px;"><strong>₹{total_amount * 0.15:.2f}</strong></td>
                                </tr>
                                <tr style="background-color: #2c3e50; color: white;">
                                    <td style="padding: 12px; font-size: 18px;">Total Amount:</td>
                                    <td style="padding: 12px; font-size: 18px;"><strong>₹{total_amount:.2f}</strong></td>
                                </tr>
                            </table>
                        </div>
                        
                        <h3 style="color: #2c3e50; margin-top: 25px; margin-bottom: 15px;">Payment Method</h3>
                        <p style="background-color: #ecf0f1; padding: 10px; border-radius: 4px; margin: 0;">
                            <strong>{payment_method.replace('_', ' ').title()}</strong>
                        </p>
                        
                        <div style="margin-top: 25px; padding: 15px; background-color: #d5f4e6; border-left: 4px solid #27ae60; border-radius: 4px;">
                            <p style="margin: 0; color: #27ae60;">
                                ✓ Your order has been confirmed. You'll receive another email once your order ships.
                            </p>
                        </div>
                        
                        <p style="margin-top: 25px; color: #7f8c8d; font-size: 12px;">
                            If you have any questions, please contact our support team at support@shopscale.com
                        </p>
                        
                        <p style="margin-top: 15px; color: #7f8c8d; font-size: 12px;">
                            Thank you for shopping with ShopScale!<br>
                            Best regards,<br>
                            ShopScale Team
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html_content


# Create global email service instance
email_service = EmailService()
