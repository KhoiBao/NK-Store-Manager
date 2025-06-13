from src.view.Login import NKManagerApp
from src.service.PM import ProductManager
from src.utils.user_manager import UserManager
from src.models.send_otp_gmail import OTPManager
if __name__ == "__main__":
    user_manager = UserManager()
    product_manager = ProductManager()
    otp_manager = OTPManager()

    app = NKManagerApp(user_manager, product_manager, otp_manager)
    app.root.mainloop()
    