from models.send_otp_gmail import OTPManager as GmailSender

class OTPManager:
    def __init__(self):
        self.current_otp = None

    def send(self, email):
        otp = GmailSender()
        self.current_otp = otp.send_otp(email)
        return self.current_otp

    def verify(self, entered_code):
        return self.current_otp == entered_code
