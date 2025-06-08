import os
import smtplib
import secrets
import json
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from email.utils import formataddr

class OTPManager:
    def __init__(self):
        load_dotenv()
        self.sender_email = os.getenv("EMAIL")
        self.sender_password = os.getenv("APP_PASSWORD")

        if not self.sender_email or not self.sender_password:
            raise Exception("⚠️ Thiếu EMAIL hoặc APP_PASSWORD trong file .env")

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_dir = os.path.join(self.base_dir, "JSON")
        self.otp_code = None

    def validate_email(self, email: str) -> str:
        if "@" not in email:
            email += "@gmail.com"

        gmail_regex = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(gmail_regex, email):
            raise ValueError("⚠️ Email không hợp lệ hoặc không phải Gmail!")

        # Cho phép mọi Gmail hợp lệ, không check tồn tại trong hệ thống
        return email

    def get_username_by_email(self, email: str):
        """Tìm username tương ứng với email từ file JSON"""
        all_files = ["admin.json", "user.json"]

        try:
            for filename in all_files:
                file_path = os.path.join(self.json_dir, filename)
                if not os.path.exists(file_path):
                    continue

                with open(file_path, "r", encoding="utf-8-sig") as file:
                    users = json.load(file)

                for user in users:
                    if user.get("email", "").strip().lower() == email.lower():
                        return user.get("username")
            return None

        except json.JSONDecodeError:
            raise ValueError("❌ Lỗi định dạng file người dùng.")
        except Exception as e:
            raise Exception(f"❌ Đã xảy ra lỗi: {e}")

    def generate_otp(self) -> str:
        """Sinh mã OTP 6 chữ số"""
        self.otp_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        return self.otp_code

    def build_html_template(self, otp_code: str) -> str:
        """Tạo template HTML cho email OTP"""
        return f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <title>OTP Email</title>
            <style>
                body {{
                    background: linear-gradient(to right, #f2f7ff, #eaf2ff);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background-color: #fff;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    padding: 40px;
                    text-align: center;
                }}
                .title {{
                    font-size: 28px;
                    font-weight: 700;
                    color: #4caf50;
                }}
                .otp-code {{
                    font-size: 42px;
                    color: #e53935;
                    font-weight: bold;
                    border: 2px dashed #e57373;
                    padding: 15px 30px;
                    border-radius: 8px;
                    display: inline-block;
                    margin: 20px 0;
                    background: #fff3f3;
                }}
                .footer {{
                    margin-top: 40px;
                    font-size: 12px;
                    color: #999;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="title">🔐 Mã Xác Thực OTP</div>
                <p>Xin chào! Đây là mã OTP của bạn:</p>
                <div class="otp-code">{otp_code}</div>
                <p>Vui lòng sử dụng mã này trong vòng <strong>2 phút</strong>.</p>
                <div class="footer">Email được gửi bởi hệ thống 💌 NK Manager.</div>
            </div>
        </body>
        </html>
        """

    def send_otp(self, email: str) -> str:
        """Gửi mã OTP qua Gmail"""
        email = self.validate_email(email)
        otp_code = self.generate_otp()
        html_body = self.build_html_template(otp_code)

        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr(("💌 NK Manager", self.sender_email))
        msg["To"] = email
        msg["Subject"] = "Mã xác nhận OTP từ hệ thống"
        msg.attach(MIMEText(html_body, "html"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, email, msg.as_string())
            server.quit()
            return otp_code

        except smtplib.SMTPAuthenticationError:
            raise Exception("❌ Không thể đăng nhập Gmail (sai App Password).")
        except smtplib.SMTPConnectError:
            raise Exception("❌ Không thể kết nối đến máy chủ Gmail.")
        except Exception as e:
            raise Exception(f"❌ Gửi email thất bại: {e}")
