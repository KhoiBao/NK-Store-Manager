import os
import sys
import customtkinter as ctk
from src.views.login import LoginView

def main():
    # Initialize application
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("NK Storage Manager")
    
    # Set up paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)
    
    # Create and show login view
    login_view = LoginView(root)
    login_view.pack(expand=True, fill="both")
    
    root.mainloop()

if __name__ == "__main__":
    main()