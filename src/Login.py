import tkinter as tk
import customtkinter as ctk
import json
import os
import re
import random
from PIL import Image, ImageTk
from tkinter import messagebox
from models.send_otp_gmail import OTPManager
import bcrypt
from utils.user_manager import UserManager
from src.PM import ProductManager
from src.product_frame import ProductFrame 
from src.product_frame import ProductFrame

class NKManagerApp:
    def __init__(self, root, login_frame, show_sign_in_callback):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.custom_theme_path = "custom_theme.json"
        try:
            with open(self.custom_theme_path, "r") as f:
                custom_theme = json.load(f)
            ctk.set_default_color_theme(self.custom_theme_path)
        except:
            pass

        self.root = ctk.CTk()
        self.root.title("NK MANAGER")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.JSON_DIR = os.path.join(self.BASE_DIR, "JSON")
        self.otp_code = None
        self.otp_expired = False
        self.user_data_temp = None
        self.user_data_for_otp = None

        self.setup_ui()
        self.show_sign_in()
        self.root.mainloop()

        self.root = root
        self.login_frame = login_frame
        self.show_sign_in = show_sign_in_callback

        self.otp_code = None
        self.otp_expired = False
        self.countdown = 120
        self.otp_timer_id = None

        self.build_forgot_password_frame()
        self.build_otp_frame()
        self.build_update_account_frame()

    def setup_ui(self):
        self.left_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.right_frame = ctk.CTkFrame(self.root, fg_color="#1e2b3a")
        self.right_frame.pack(side="right", fill="y")

        self.full_frame = ctk.CTkFrame(self.root, fg_color="#1e2b3a")
        self.full_frame.pack_forget()

        try:
            bg_image = Image.open("Picture NK Manager.png")
            image_ratio = bg_image.width / bg_image.height
            resized_height = int(self.root.winfo_screenheight() * 1.8)
            resized_width = int(resized_height * image_ratio)
            bg_image = bg_image.resize((resized_width, resized_height), Image.Resampling.LANCZOS)
            bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = ctk.CTkLabel(self.left_frame, image=bg_photo, text="")
            bg_label.image = bg_photo
            bg_label.place(relx=0.5, rely=0.5, anchor="center")
        except:
            self.left_frame.configure(fg_color="#2c3e50")

        self.login_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.login_frame.pack(padx=60, pady=60, expand=True, fill="both")

        self.build_sign_in_frame()
        self.build_sign_up_frames()
        self.build_forgot_password_frame()
        self.build_otp_frame()
        self.build_update_account_frame()

#===============================================================================
# ============================= Đăng nhập ======================================
#===============================================================================

    def build_sign_in_frame(self):
        self.sign_in_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        ctk.CTkLabel(self.sign_in_frame, text="🔐 Đăng nhập", font=("Segoe UI", 28, "bold"), text_color="#1abc9c").pack(pady=30)
        
        # Nhãn cho tên tài khoản
        ctk.CTkLabel(self.sign_in_frame, text="Tên tài khoản (*)", text_color="white", anchor="w").pack(anchor="w", padx=0)
        self.entry_username_sign_in = ctk.CTkEntry(self.sign_in_frame, placeholder_text="Tên tài khoản", width=300)
        self.entry_username_sign_in.pack(pady=10)

        # Nhãn cho mật khẩu
        label_password = ctk.CTkLabel(self.sign_in_frame, text="Mật khẩu (*)", text_color="white", anchor="w")
        label_password.pack(anchor="w", padx=0)

        # Frame chứa Entry + nút 👁
        self.password_frame = ctk.CTkFrame(self.sign_in_frame, fg_color="transparent")
        self.password_frame.pack(pady=10)

        # Entry mật khẩu
        self.entry_password_sign_in = ctk.CTkEntry(self.password_frame, placeholder_text="Mật khẩu", show="*", width=260)
        self.entry_password_sign_in.pack(side="left")

        # Nút 👁 hiện/ẩn mật khẩu
        def toggle_password__():
            if self.entry_password_sign_in.cget("show") == "":
                self.entry_password_sign_in.configure(show="*")
                self.toggle_button__.configure(text="👁")
            else:
                self.entry_password_sign_in.configure(show="")
                self.toggle_button__.configure(text="🙈")

        self.toggle_button__ = ctk.CTkButton(
            self.password_frame,
            text="👁",
            width=30,
            command=toggle_password__,
            fg_color="transparent",
            hover_color="#34495e"
        )
        self.toggle_button__.pack(side="left", padx=5)

        # ===== Đăng nhập sau khi kiểm tra =====
        self.sign_in_button = ctk.CTkButton(
            self.sign_in_frame, 
            text="Đăng nhập", 
            width=300, 
            fg_color="#1abc9c", 
            hover_color="#161fa0", 
            command=self.handle_login
        )
        self.sign_in_button.pack(pady=15)

        # ===== Label chuyển sang đăng ký =====
        label_switch_to_sign_up = ctk.CTkLabel(self.sign_in_frame, text="Bạn chưa có tài khoản? Đăng ký tại đây.", text_color="#00acee", cursor="hand2")
        label_switch_to_sign_up.pack(pady=(20, 0))
        label_switch_to_sign_up.bind("<Enter>", lambda e: label_switch_to_sign_up.configure(text_color="#1abc9c"))
        label_switch_to_sign_up.bind("<Leave>", lambda e: label_switch_to_sign_up.configure(text_color="#00acee"))
        label_switch_to_sign_up.bind("<Button-1>", lambda e: self.show_sign_up())

        # ===== Label chuyển sang quên mật khẩu =====
        forget_password_label = ctk.CTkLabel(self.sign_in_frame, text="Bạn quên mật khẩu?", text_color="#e74c3c", cursor="hand2")
        forget_password_label.pack()
        forget_password_label.bind("<Enter>", lambda e: forget_password_label.configure(text_color="#f39c12"))
        forget_password_label.bind("<Leave>", lambda e: forget_password_label.configure(text_color="#e74c3c"))
        forget_password_label.bind("<Button-1>", lambda e: self.show_forgot_password())

        # ===== Return =====
        self.entry_username_sign_in.bind("<Return>", lambda e: self.entry_password_sign_in.focus())
        self.entry_password_sign_in.bind("<Return>", lambda e: self.handle_login())

#===============================================================================
# ============================= Đăng ký tài khoản ==============================
#===============================================================================

# ==== 1. Kiểm tra hợp lệ tên tài khoản, email, mật khẩu, mã cửa hàng ====
    def validate_user_input(self, username, email, password, confirm_pw, store_code):
        email = str(email).strip()
        username = str(username).strip()
        store_code = str(store_code).strip()

        if not username:
            return "Vui lòng nhập tên tài khoản."
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            return "Tên tài khoản chỉ được chứa chữ cái và số."

        if not email:
            return "Vui lòng nhập Gmail."
        if not re.match(r'^[\w\.-]+@gmail\.com$', email):
            return "Gmail không hợp lệ."

        if self.email_exists(email):
            return "Gmail đã được đăng ký."

        if not password:
            return "Vui lòng nhập mật khẩu."
        if not self.is_strong_password(password):
            return "Mật khẩu phải từ 8-15 ký tự, gồm chữ hoa, thường, số và ký tự đặc biệt."
        if password != confirm_pw:
            return "Mật khẩu nhập lại không khớp."

        if not store_code:
            return "Vui lòng nhập mã cửa hàng."
        if not self.store_code_exists(store_code):
            return "Mã cửa hàng không tồn tại."

        self.temp_user_data = {
        "username": username,
        "email": email,
        "password": password,
        "store_code": store_code
        }

        # Gửi OTP và chuyển sang giao diện OTP
        if self.send_signup_otp():
            self.show_otp_frame()
            self.start_otp_timer()
            return "OK"
        else:
            return "Không thể gửi mã OTP."

    # ==== 2. Kiểm tra độ mạnh mật khẩu ====
    def is_strong_password(self, pw):
        return 8 <= len(pw) <= 15 and \
               re.search(r'[A-Z]', pw) and \
               re.search(r'[a-z]', pw) and \
               re.search(r'\d', pw) and \
               re.search(r'[^\w\s]', pw)

    # ==== 3. Kiểm tra trùng Gmail trong user/admin.json ====
    def email_exists(self, email):
        for filename in ['user.json', 'admin.json']:
            path = os.path.join(self.JSON_DIR, filename)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if any(user.get("email") == email for user in data):
                            return True
                    except json.JSONDecodeError:
                        continue
        return False

    # ==== 4. Kiểm tra mã cửa hàng có tồn tại trong admin.json không ====
    def store_code_exists(self, store_code):
        path = os.path.join(self.JSON_DIR, "admin.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    return any(admin.get("store_code") == store_code for admin in data)
                except json.JSONDecodeError:
                    return False
        return False

    # ==== 5. Tạo mã OTP ngẫu nhiên ====
    def generate_otp(self):
        self.otp_code = str(random.randint(100000, 999999))
        self.otp_expired = False
        return self.otp_code

    # ==== 6. Xác thực mã OTP ====
    def verify_otp(self, entered_otp):
        if self.otp_expired:
            return "OTP đã hết hạn"
        return "OK" if entered_otp == self.otp_code else "Sai OTP"

    # ==== 7. Lưu người dùng vào user.json ====
    def save_user(self):
        if not self.temp_user_data:
            return "Không có dữ liệu để lưu."

        path = os.path.join(self.JSON_DIR, "user.json")
        user_list = []

        # Đọc dữ liệu cũ
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    user_list = json.load(f)
                except json.JSONDecodeError:
                    user_list = []

        # Ghi dữ liệu mới
        user_list.append(self.temp_user_data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(user_list, f, indent=4, ensure_ascii=False)

        return "Đăng ký thành công!"    

    def build_sign_up_frames(self):
        self.sign_up_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        ctk.CTkLabel(self.sign_up_frame, text="📝 Đăng ký tài khoản", font=("Segoe UI", 28, "bold"), text_color="#1abc9c").pack(pady=(0, 30))

        # Tên tài khoản
        ctk.CTkLabel(self.sign_up_frame, text="Tên tài khoản (*)", text_color="white", anchor="w").pack(anchor="w", padx=0)
        self.entry_username = ctk.CTkEntry(self.sign_up_frame, placeholder_text="Chỉ chữ và số", width=300)
        self.entry_username.pack(pady=10)

        # Gmail
        ctk.CTkLabel(self.sign_up_frame, text="Địa chỉ Gmail (*)", text_color="white", anchor="w").pack(anchor="w", padx=0)
        self.entry_email_signup = ctk.CTkEntry(self.sign_up_frame, placeholder_text="Địa chỉ Gmail", width=300)
        self.entry_email_signup.pack(pady=10)

        # Mật khẩu
        label_password = ctk.CTkLabel(self.sign_up_frame, text="Mật khẩu (*)", text_color="white", anchor="w")
        label_password.pack(anchor="w", padx=0)
    
        # Frame chứa Entry + nút 👁
        self.password_sign_up = ctk.CTkFrame(self.sign_up_frame, fg_color="transparent")
        self.password_sign_up.pack(pady=10)

        # Entry mật khẩu
        self.entry_password_sign_up = ctk.CTkEntry(self.password_sign_up, placeholder_text="8-15 ký tự, hoa, thường, số, đặc biệt", show="*", width=260)
        self.entry_password_sign_up.pack(side="left")

        # Nút 👁 hiện/ẩn mật khẩu
        def toggle_password():
            if self.entry_password_sign_up.cget("show") == "":
                self.entry_password_sign_up.configure(show="*")
                self.toggle_button.configure(text="👁")
            else:
                self.entry_password_sign_up.configure(show="")
                self.toggle_button.configure(text="🙈")

        self.toggle_button = ctk.CTkButton(
            self.password_sign_up,
            text="👁",
            width=30,
            command=toggle_password,
            fg_color="transparent",
            hover_color="#34495e"
        )
        self.toggle_button.pack(side="left", padx=5)   

        # Nhập lại mật khẩu
        # Mật khẩu
        label_password = ctk.CTkLabel(self.sign_up_frame, text="Nhập lại mật khẩu (*)", text_color="white", anchor="w")
        label_password.pack(anchor="w", padx=0)
    
        # Frame chứa Entry + nút 👁
        self.confirm_frame = ctk.CTkFrame(self.sign_up_frame, fg_color="transparent")
        self.confirm_frame.pack(pady=10)

        # Entry mật khẩu
        self.entry_confirm_password_ = ctk.CTkEntry(self.confirm_frame, placeholder_text="8-15 ký tự, hoa, thường, số, đặc biệt", show="*", width=260)
        self.entry_confirm_password_.pack(side="left")

        # Nút 👁 hiện/ẩn mật khẩu
        def toggle_password_():
            if self.entry_confirm_password_.cget("show") == "":
                self.entry_confirm_password_.configure(show="*")
                self.toggle_button_.configure(text="👁")
            else:
                self.entry_confirm_password_.configure(show="")
                self.toggle_button_.configure(text="🙈")

        self.toggle_button_ = ctk.CTkButton(
            self.confirm_frame,
            text="👁",
            width=30,
            command=toggle_password_,
            fg_color="transparent",
            hover_color="#34495e"
        )
        self.toggle_button_.pack(side="left", padx=5)  

        # Mã cửa hàng
        ctk.CTkLabel(self.sign_up_frame, text="Mã cửa hàng (*)", text_color="white", anchor="w").pack(anchor="w", padx=0)
        self.entry_store_code = ctk.CTkEntry(self.sign_up_frame, placeholder_text="Nhập mã cửa hàng", width=300)
        self.entry_store_code.pack(pady=10)

        # Nút tiếp theo
        next_button_sign_up = ctk.CTkButton(self.sign_up_frame, text="Tiếp theo", width=300, fg_color="#1abc9c", hover_color="#1634a0", command=self.handle_signup_next)
        next_button_sign_up.pack(pady=20)
        self.entry_email_signup.bind("<Return>", lambda event: self.send_signup_otp())

        # Đường dẫn quay về đăng nhập
        label_switch_to_sign_in_from_signup = ctk.CTkLabel(self.sign_up_frame, text="Bạn đã có tài khoản? Đăng nhập tại đây.", text_color="#00acee", cursor="hand2")
        label_switch_to_sign_in_from_signup.pack() 
        label_switch_to_sign_in_from_signup.bind("<Enter>", lambda e: label_switch_to_sign_in_from_signup.configure(text_color="#1abc9c"))
        label_switch_to_sign_in_from_signup.bind("<Leave>", lambda e: label_switch_to_sign_in_from_signup.configure(text_color="#00acee"))
        label_switch_to_sign_in_from_signup.bind("<Button-1>", lambda e: self.show_sign_in())

        # Bind enter để nhảy xuống từng ô
        self.entry_username.bind("<Return>", lambda e: self.entry_email_signup.focus())
        self.entry_email_signup.bind("<Return>", lambda e: self.entry_password_sign_up.focus())
        self.entry_password_sign_up.bind("<Return>", lambda e: self.entry_confirm_password_.focus())
        self.entry_confirm_password_.bind("<Return>", lambda e: self.entry_store_code.focus())
        self.entry_store_code.bind("<Return>", lambda e: self.handle_signup_next())


    # ==== Gửi OTP sau đăng ký ====
    def send_signup_otp(self):
        self.is_signup_otp = True
        try:
            otp_manager = OTPManager()
            email = self.temp_user_data.get("email")
            validated_email = otp_manager.validate_email(email)
            self.otp_code = otp_manager.send_otp(validated_email)
            self.otp_expired = False
            if self.otp_code:
                print(f"✅ OTP đăng ký đã gửi: {self.otp_code}")
                return True
            else:
                print("❌ Gửi OTP thất bại.")
                return False
        except Exception as e:
            print(f"❌ Lỗi gửi OTP đăng ký: {e}")
            return False

    # ==== Xác thực OTP đăng ký ====
    def verify_signup_otp(self, entered_otp):
        if self.otp_expired:
            return "OTP đã hết hạn"
        if entered_otp == self.otp_code:
            result = self.save_signup_user()
            return result
        else:
            return "Sai OTP"

    # ==== Lưu user sau OTP thành công ====
    def save_signup_user(self):
        path = os.path.join(self.JSON_DIR, "user.json")
        user_list = []
        hashed_pw = bcrypt.hashpw(
            self.temp_user_data["password"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
        self.temp_user_data["password"] = hashed_pw

        # Đọc dữ liệu cũ
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    user_list = json.load(f)
                except json.JSONDecodeError:
                    user_list = []

        # Ghi dữ liệu mới
        user_list.append(self.temp_user_data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(user_list, f, indent=4, ensure_ascii=False)

        print("✅ Đăng ký thành công và đã lưu vào user.json!")
        return "Đăng ký thành công!"

    def handle_signup_next(self):
        result = self.validate_user_input(
            self.entry_username.get(),
            self.entry_email_signup.get(),
            self.entry_password_sign_up.get(),
            self.entry_confirm_password_.get(),
            self.entry_store_code.get()
        )
        print("Signup next result:", result)
        if result != "OK":
            messagebox.showwarning("Cảnh báo", result)


    def build_forgot_password_frame(self):
        # ... Cài đặt giao diện quên mật khẩu (OOP hóa)
        pass

    def build_otp_frame(self):
        # ... Cài đặt giao diện OTP (OOP hóa)
        pass

    def build_update_account_frame(self):
        # ... Cài đặt giao diện đổi mật khẩu / tài khoản (OOP hóa)
        pass

    def show_sign_in(self):
        #self.hide_all_frames()
        self.sign_up_frame.pack_forget()
        #self.forgot_password_frame.pack_forget()
        #self.otp_frame.pack_forget()
        #self.update_account_frame.pack_forget()
        self.login_frame.pack()
        self.sign_in_frame.pack(fill="both", expand=True)

    def show_sign_up(self):
        #self.hide_all_frames()
        self.sign_in_frame.pack_forget()
        self.sign_up_frame.pack(fill="both", expand=True)

    def build_forgot_password_frame(self):
        self.forgot_password_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        ctk.CTkLabel(self.forgot_password_frame, text="🔑 Gửi lại mật khẩu", font=("Segoe UI", 28, "bold"), text_color="#1abc9c").pack(pady=(0, 30))

        ctk.CTkLabel(self.forgot_password_frame, text="Nhập địa chỉ Gmail (*)", text_color="white", anchor="w").pack(anchor="w", padx=0)
        self.entry_email_forgot = ctk.CTkEntry(self.forgot_password_frame, placeholder_text="Nhập địa chỉ Gmail", width=300)
        self.entry_email_forgot.pack(pady=10)

        next_button = ctk.CTkButton(self.forgot_password_frame, text="Tiếp theo", width=300, fg_color="#1abc9c", hover_color="#1634a0", command=self.send_otp_email_action_forgot)
        next_button.pack(pady=20)

        self.entry_email_forgot.bind("<Return>", lambda event: self.send_otp_email_action_forgot())

        back_button_label = ctk.CTkLabel(self.forgot_password_frame, text="Quay lại màn hình chính", text_color="#e74c3c", cursor="hand2")
        back_button_label.pack()
        back_button_label.bind("<Enter>", lambda e: back_button_label.configure(text_color="#f39c12"))
        back_button_label.bind("<Leave>", lambda e: back_button_label.configure(text_color="#e74c3c"))
        back_button_label.bind("<Button-1>", lambda e: self.back_to_sign_in())

    def build_otp_frame(self):
        self.otp_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        ctk.CTkLabel(self.otp_frame, text="🔑 Xác minh OTP", font=("Segoe UI", 28, "bold"), text_color="#1abc9c").pack(pady=(0, 30))

        ctk.CTkLabel(self.otp_frame, text="Nhập mã OTP vừa gửi qua Gmail (*)", text_color="white", anchor="w").pack(anchor="w", padx=0)
        self.entry_otp = ctk.CTkEntry(self.otp_frame, placeholder_text="Nhập mã OTP", width=300)
        self.entry_otp.pack(pady=10)
        self.entry_otp.bind("<Return>", lambda event: self.verify_otp_action())

        self.otp_timer_label = ctk.CTkLabel(self.otp_frame, text="Thời gian còn lại: 2:00", text_color="#e67e22", font=("Segoe UI", 14))
        self.otp_timer_label.pack(pady=(5, 5))

        self.resend_otp_button = ctk.CTkButton(self.otp_frame, text="Gửi lại mã OTP", fg_color="transparent", hover_color="#16a085", command=self.resend_otp, state="disabled")
        self.resend_otp_button.pack(pady=(10, 5))

        self.submit_otp_button = ctk.CTkButton(self.otp_frame, text="Xác nhận", width=300, fg_color="#1abc9c", hover_color="#1632a0", command=self.verify_otp_action)
        self.submit_otp_button.pack(pady=20)

        self.entry_otp.bind("<Return>", lambda event: self.verify_otp_action())

        back_label = ctk.CTkLabel(self.otp_frame, text="Quay lại trang quên mật khẩu", text_color="#00acee", cursor="hand2")
        back_label.pack(pady=(20, 0))
        back_label.bind("<Enter>", lambda e: back_label.configure(text_color="#1abc9c"))
        back_label.bind("<Leave>", lambda e: back_label.configure(text_color="#00acee"))
        back_label.bind("<Button-1>", lambda e: self.show_forgot_password())

    def build_update_account_frame(self):
        self.update_account_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        ctk.CTkLabel(self.update_account_frame, text="🔧 Đổi mật khẩu", font=("Segoe UI", 28, "bold"), text_color="#1abc9c").pack(pady=(0, 30))

        ctk.CTkLabel(self.update_account_frame, text="Mật khẩu mới (*)", text_color="white", anchor="w").pack(anchor="w", padx=0)
        pw_frame = ctk.CTkFrame(self.update_account_frame, fg_color="transparent")
        pw_frame.pack(pady=10)
        self.entry_new_password = ctk.CTkEntry(pw_frame, placeholder_text="Mật khẩu mới", show="*", width=260)
        self.entry_new_password.pack(side="left")
        self.show_button_pw = ctk.CTkButton(pw_frame, text="👁", width=30, command=lambda: self.toggle_password(self.entry_new_password, self.show_button_pw), fg_color="transparent", hover_color="#34495e")
        self.show_button_pw.pack(side="left", padx=5)

        ctk.CTkLabel(self.update_account_frame, text="Nhập lại mật khẩu (*)", text_color="white", anchor="w").pack(anchor="w", padx=0)
        confirm_frame = ctk.CTkFrame(self.update_account_frame, fg_color="transparent")
        confirm_frame.pack(pady=10)
        self.entry_confirm_password = ctk.CTkEntry(confirm_frame, placeholder_text="Nhập lại mật khẩu", show="*", width=260)
        self.entry_confirm_password.pack(side="left")
        self.entry_confirm_password.bind("<FocusOut>", lambda e: self.check_password_match())

        self.show_button_confirm = ctk.CTkButton(confirm_frame, text="👁", width=30, command=lambda: self.toggle_password(self.entry_confirm_password, self.show_button_confirm), fg_color="transparent", hover_color="#34495e")
        self.show_button_confirm.pack(side="left", padx=5)

        self.update_button = ctk.CTkButton(self.update_account_frame, text="Cập nhật thông tin", width=300, fg_color="#1abc9c", hover_color="#1622a0", command=self.update_account_action)
        self.update_button.pack(pady=20)

        self.entry_new_password.bind("<Return>", lambda e: self.entry_confirm_password.focus())
        self.entry_confirm_password.bind("<Return>", lambda e: self.update_account_action())

        back_button_label = ctk.CTkLabel(self.update_account_frame, text="Quay lại màn hình chính", text_color="#e74c3c", cursor="hand2")
        back_button_label.pack()
        back_button_label.bind("<Enter>", lambda e: back_button_label.configure(text_color="#f39c12"))
        back_button_label.bind("<Leave>", lambda e: back_button_label.configure(text_color="#e74c3c"))
        back_button_label.bind("<Button-1>", lambda e: self.back_to_sign_in())

    def check_password_match(self):
        pw = self.entry_new_password.get()
        confirm = self.entry_confirm_password.get()
        if pw and confirm and pw != confirm:
            messagebox.showwarning("Cảnh báo", "⚠️ Mật khẩu nhập lại không khớp!")
    
    def show_forgot_password(self):
        self.hide_all_frames()
        self.forgot_password_frame.pack(fill="both", expand=True)

    def send_otp_email_action_forgot(self):
        from send_otp_gmail import OTPManager  
        self.is_signup_otp = False
        email = self.entry_email_forgot.get().strip()

        if not email:
            messagebox.showwarning("Vui lòng nhập lại địa chỉ Gmail.")
            return 
        
        user_manage = UserManager()
        if not user_manage.email_exists(email):
            messagebox.showerror("Lỗi","Tài khoản không tồn tại, vui lòng đăng ký tài khoản.")
            return
        
        try:
            otp_manager = OTPManager()
            validated_email = otp_manager.validate_email(email)
            self.otp_code = otp_manager.send_otp(validated_email)
            self.otp_expired = False
            if self.otp_code:
                self.show_otp_frame()
                print(f"✅ OTP sent successfully: {self.otp_code}")
                self.start_otp_timer()
            else:
                messagebox.showerror("Lỗi", "Không thể gửi mã OTP. Vui lòng thử lại.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"❌ {str(e)}")        

    def start_otp_timer(self):
        self.countdown = 120
        self.update_timer()

    def update_timer(self):
        minutes = self.countdown // 60
        seconds = self.countdown % 60
        self.otp_timer_label.configure(text=f"Thời gian còn lại: {minutes}:{seconds:02d}")

        if self.countdown > 0:
            self.countdown -= 1
            self.otp_timer_id = self.root.after(1000, self.update_timer)
        else:
            self.otp_expired = True
            self.otp_timer_label.configure(text="Mã OTP đã hết hạn!")
            self.resend_otp_button.configure(state="normal")

    def resend_otp(self):
        self.resend_otp_button.configure(state="disabled")
        self.send_otp_email_action_forgot()

    def verify_otp_action(self):
        if self.otp_expired:
            messagebox.showerror("Lỗi", "Mã OTP đã hết hạn! Vui lòng yêu cầu mã mới.")
            return

        entered_otp = self.entry_otp.get().strip()
        if entered_otp != self.otp_code:
            messagebox.showerror("Lỗi", "Mã OTP không chính xác. Vui lòng thử lại.")
            return

        # Phân biệt đăng ký hay quên mật khẩu
        if getattr(self, "is_signup_otp", False):  # default là False
            result = self.save_signup_user()
            messagebox.showinfo("Thành công", result)
            self.back_to_sign_in()
        else:
            self.show_update_account_frame()

    def update_account_action(self):
        new_password = self.entry_new_password.get()
        confirm_password = self.entry_confirm_password.get()

        if new_password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp!")
            return

        if not self.is_strong_password(new_password):
            messagebox.showerror("Lỗi", "Mật khẩu phải dài 8–16 ký tự, có chữ hoa, chữ thường, số và ký tự đặc biệt.")
            return

        # Update JSON file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        JSON_DIR = os.path.join(BASE_DIR, "JSON")
        users_file = os.path.join(JSON_DIR, "user.json")

        try:
            with open(users_file, "r+", encoding="utf-8") as f:
                users = json.load(f)
                email = self.entry_email.get().strip()
                for user in users:
                    if user["email"] == email:
                        user["password"] = new_password
                        break
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy người dùng.")
                    return

                f.seek(0)
                json.dump(users, f, indent=4, ensure_ascii=False)
                f.truncate()

            messagebox.showinfo("Thành công", "Tài khoản đã được cập nhật!")
            self.back_to_sign_in()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Cập nhật thất bại: {e}")

    def toggle_password(self, entry, button):
        if entry.cget("show") == "":
            entry.configure(show="*")
            button.configure(text="👁")
        else:
            entry.configure(show="")
            button.configure(text="🙈")

    def is_strong_password(self, password):
        import re
        return (8 <= len(password) <= 16 and
                re.search(r"[A-Z]", password) and
                re.search(r"[a-z]", password) and
                re.search(r"\d", password) and
                re.search(r"[^\w\s]", password))

    def hide_all_frames(self):
        self.forgot_password_frame.pack_forget()
        self.otp_frame.pack_forget()
        self.update_account_frame.pack_forget()

    def show_otp_frame(self):
        self.hide_all_frames()
        self.otp_frame.pack(fill="both", expand=True)

    def show_update_account_frame(self):
        self.hide_all_frames()
        self.update_account_frame.pack(fill="both", expand=True)

    def back_to_sign_in(self):
        self.hide_all_frames()
        self.show_sign_in()

    def hide_all_frames(self):
        for frame in [
            self.sign_in_frame,
            self.sign_up_frame,
            self.forgot_password_frame,
            self.otp_frame,
            self.update_account_frame
        ]:
            frame.pack_forget()

    def handle_login(self):
        username = self.entry_username_sign_in.get()
        password = self.entry_password_sign_in.get()
        role = self.verify_login(username, password)
        if role == "admin":
            self.show_admin_page()
        elif role == "user":
            self.show_user_page()
        else:
            messagebox.showerror("Lỗi", "Tên tài khoản hoặc mật khẩu không đúng!")

    def verify_login(self, username, password):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.JSON_DIR = os.path.join(self.BASE_DIR, "JSON")

        # Kiểm tra các file người dùng và admin
        for file in ["admin.json", "user.json"]:
            file_path = os.path.join(self.JSON_DIR, file)
            if not os.path.exists(file_path):
                continue
            
            try:
                # Đọc dữ liệu từ file JSON
                with open(file_path, "r", encoding="utf-8") as f:
                    users = json.load(f)
                    
                    # Duyệt qua từng user trong danh sách
                    for u in users:
                        if u["username"] != username:
                            continue
                        
                        stored_password = u["password"]

                        # ✅ Trường hợp mật khẩu đã được băm (bcrypt)
                        if isinstance(stored_password, str) and (stored_password.startswith("$2b$") or stored_password.startswith("$2a$")):
                            if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
                                return file.replace(".json", "")
                        
                        # ✅ Trường hợp mật khẩu là dạng plain text
                        elif stored_password == password:
                            return file.replace(".json", "")
            except Exception as e:
                print(f"⚠️ Lỗi khi đọc {file_path}: {e}")

        # Nếu không tìm thấy tài khoản hoặc mật khẩu sai
        return None
    
    def show_admin_page(self):
        self.left_frame.pack_forget()
        self.right_frame.pack_forget()
        
        self.full_frame.pack(fill="both", expand=True)
        for widget in self.full_frame.winfo_children():
            widget.destroy()

        product_ui = ProductFrame(self.full_frame, controller=None, role="admin")
        product_ui.pack(fill="both", expand=True)

        logout_button = ctk.CTkButton(
                self.full_frame,
                text="🚪 Đăng xuất",
                command=self.logout_action,
                fg_color="red",     
                text_color="white"
        )
        logout_button.pack(pady=20)

    def show_user_page(self):
        self.left_frame.pack_forget()
        self.right_frame.pack_forget()

        self.full_frame.pack(fill="both", expand=True)
        for widget in self.full_frame.winfo_children():
            widget.destroy()

        product_ui = ProductFrame(self.full_frame, controller=None, role="user")
        product_ui.pack(fill="both", expand=True)

        logout_button = ctk.CTkButton(
            self.full_frame,
            text="🚪 Đăng xuất",
            command=self.logout_action,
            fg_color="red",     
            text_color="white"
        )
        logout_button.pack(pady=20)
 
    def logout_action(self):
        try:
            # Ẩn toàn bộ các frame cũ
            for frame in [self.full_frame, self.left_frame, self.right_frame]:
                if frame.winfo_exists():
                    frame.pack_forget()
            
            # Hiện lại giao diện đăng nhập
            self.left_frame.pack(side="left", fill="both", expand=True)
            self.right_frame.pack(side="right", fill="y")
            self.show_sign_in()
        except Exception as e:
            print("Lỗi khi đăng xuất:", e)