import os
import json
import shutil
from PIL import Image
import customtkinter as ctk
from src.models.products import Product
from tkinter import messagebox,filedialog
from src.service.PM import ProductManager


class ProductFrame(ctk.CTkFrame):
    def __init__(self, master, controller, role="user"):
        super().__init__(master)
        self.controller = controller
        self.role = role

        self.product_manager = controller.product_manager

        self.sort_by = None
        self.sort_order = "asc"
        self.admin_username = getattr(self.controller, "admin_username", "admin")
        # Configure grid weights for responsive layout
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()
        self.load_products()
        
    def show_admin_info(self):
        # Lấy thông tin admin từ file admin.json
        admin_info = None
        store_name = ""  
        store_code = "CH000"
        
        try:
            # Đọc file admin.json
            admin_file_path = os.path.abspath("admin.json")
            if os.path.exists(admin_file_path):
                with open(admin_file_path, 'r', encoding='utf-8') as f:
                    admin_data = json.load(f)
                    if admin_data and len(admin_data) > 0:
                        admin_info = admin_data[0]  # Lấy admin đầu tiên
            
            # Nếu không có file admin.json, thử lấy từ user_manager
            if not admin_info and hasattr(self.controller, 'user_manager'):
                users = self.controller.user_manager.list()
                for user in users:
                    if user.get("role") == "admin":
                        admin_info = user
                        break
        except Exception as e:
            print(f"Lỗi đọc file admin.json: {e}")
        
        # Lấy thông tin cửa hàng từ admin_info
        if admin_info:
            store_name = admin_info.get("store_name", "Cửa hàng")
            store_code = admin_info.get("store_code", "CH000")
            admin_fullname = admin_info.get("fullname", "Admin")
            admin_email = admin_info.get("email", "")
            admin_username = admin_info.get("username", "")
        else:
            admin_fullname = "Admin"
            admin_email = ""
            admin_username = ""

        # Giao diện hiển thị
        popup = ctk.CTkToplevel(self)
        popup.title("Thông tin quản trị viên")
        popup.geometry("650x600")
        popup.resizable(False, False)

        # Tiêu đề với thông tin cửa hàng
        header_text = f"Danh sách người dùng - {store_name} (Mã: {store_code})"
        
        ctk.CTkLabel(
            popup,
            text=header_text,
            font=("Segoe UI", 18, "bold"),
            text_color="#1abc9c"
        ).pack(pady=(10, 5))
        
        # Thông tin admin
        admin_info_frame = ctk.CTkFrame(popup, fg_color="#2b2b2b", corner_radius=10)
        admin_info_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        ctk.CTkLabel(
            admin_info_frame,
            text=f"Quản trị viên: {admin_fullname}",
            font=("Segoe UI", 14, "bold"),
            text_color="#3498db"
        ).pack(pady=(10, 2))
        
        if admin_username:
            ctk.CTkLabel(
                admin_info_frame,
                text=f"Username: {admin_username}",
                font=("Segoe UI", 12),
                text_color="#95a5a6"
            ).pack(pady=(0, 2))
        
        if admin_email:
            ctk.CTkLabel(
                admin_info_frame,
                text=f"Email: {admin_email}",
                font=("Segoe UI", 12),
                text_color="#95a5a6"
            ).pack(pady=(0, 10))

        info_frame = ctk.CTkFrame(popup)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Danh sách user (không bao gồm admin)
        user_list_frame = ctk.CTkScrollableFrame(info_frame, label_text="Danh sách người dùng")
        user_list_frame.pack(fill="both", expand=True, pady=(10, 10))

        if hasattr(self.controller, 'user_manager'):
            users = self.controller.user_manager.list()
            user_count = 0
            for idx, user in enumerate(users):
                if user.get("role") == "admin":
                    continue
                
                user_count += 1
                row = ctk.CTkFrame(user_list_frame)
                row.pack(fill="x", pady=2, padx=5)

                display_text = f"{user.get('fullname', '')} ({user.get('email', '')})"
                ctk.CTkLabel(row, text=display_text, font=("Segoe UI", 12)).pack(side="left", padx=10)
                
                del_btn = ctk.CTkButton(
                    row,
                    text="Xóa",
                    width=60,
                    fg_color="#e74c3c",
                    hover_color="#c0392b",
                    command=lambda u=user: self.delete_user(u.get("email", ""), popup)
                )
                del_btn.pack(side="right", padx=10)
            
            # Hiển thị số lượng user
            if user_count == 0:
                empty_label = ctk.CTkLabel(
                    user_list_frame,
                    text="Chưa có người dùng nào",
                    font=("Segoe UI", 14),
                    text_color="gray"
                )
                empty_label.pack(pady=20)
            else:
                count_label = ctk.CTkLabel(
                    popup,
                    text=f"Tổng số người dùng: {user_count}",
                    font=("Segoe UI", 12),
                    text_color="#7f8c8d"
                )
                count_label.pack(pady=(0, 10))
    def delete_user(self, email, popup):
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa người dùng '{email}'?")
        if confirm:
            self.controller.user_manager.delete(email)
            messagebox.showinfo("Thành công", f"Đã xóa người dùng '{email}'")
            popup.destroy()
            self.show_admin_info()

    

    def build_ui(self):
        # Header section with logo and title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)
        greeting = ctk.CTkLabel(self,text=f"Xin chào, {self.role}!",font=("Segoe UI",16,"bold"),text_color="#32AAF0",anchor="w")
        greeting.grid(row = 1,column = 0, sticky="w",padx=20,pady=(10,5)) 
        greeting = ctk.CTkLabel(
            header_frame,
            text=f"👋 Xin chào, {self.role}!",
            font=("Segoe UI", 16, "bold"),
            text_color="#32AAF0",
            anchor="e"
        )
        greeting.grid(row=0, column=2, sticky="e", padx=(0, 5), pady=0)
        if self.role == "admin":
            greeting.bind("<Button-1>",lambda e: self.show_admin_info())

        # Logo
        logo_path = os.path.abspath(os.path.join("assets","Picture NK Manager.png"))

        if not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo file not found at: {logo_path}")
        
        logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(100, 100))
        logo_label = ctk.CTkLabel(header_frame, image=logo_img, text="")
        logo_label.grid(row=0, column=0, padx=(0, 15), pady=0)
        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Quản lý Sản phẩm", 
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="w")

        # Control panel
        control_frame = ctk.CTkFrame(self, corner_radius=15)
        control_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        control_frame.grid_columnconfigure(0, weight=1)

        # Search section
        search_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=15)

        search_label = ctk.CTkLabel(search_frame, text="Tìm kiếm:", font=("Segoe UI", 14, "bold"))
        search_label.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Nhập tên sản phẩm...", 
            width=300,
            height=35,
            corner_radius=8
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda e: self.search_products())

        search_btn = ctk.CTkButton(
            search_frame, 
            text="Tìm kiếm", 
            width=100,
            height=35,
            corner_radius=8,
            command=self.search_products
        )
        search_btn.pack(side="left", padx=(0, 10))

        refresh_btn = ctk.CTkButton(
            search_frame, 
            text="Làm mới", 
            width=100,
            height=35,
            corner_radius=8,
            fg_color="gray",
            hover_color="darkgray",
            command=self.load_products
        )
        refresh_btn.pack(side="left", padx=(0, 10))

        # Add product button for admin
        if self.role == "admin":
            add_btn = ctk.CTkButton(
                search_frame, 
                text="➕ Thêm sản phẩm", 
                width=140,
                height=35,
                corner_radius=8,
                fg_color="#28a745",
                hover_color="#218838",
                command=self.show_add_dialog
            )
            add_btn.pack(side="right")

        # Products display area
        self.products_frame = ctk.CTkScrollableFrame(
            self, 
            corner_radius=15,
            scrollbar_button_color="gray",
            scrollbar_button_hover_color="darkgray"
        )
        self.products_frame.grid(row=2, column=0, sticky="nsew", padx=(10,0), pady=(0, 20))

    def create_product_header(self):
        """Create a modern header for the product list"""
        header = ctk.CTkFrame(self.products_frame, height=50, corner_radius=10)
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        # Configure grid
        for i in range(6):
            header.grid_columnconfigure(i, weight=1, uniform="col")

        # Header labels with better styling
        headers = [
            ("Tên sản phẩm", 0),
            ("Mô tả", 1), 
            ("Danh mục", 2),
            ("Số lượng", 3),
            ("Giá", 4),
            ("Thao tác", 5)
        ]

        for text, col in headers:
            if col == 3:  # Quantity sort button
                self.soluong_sort_btn = ctk.CTkButton(
                    header, 
                    text=f"Số lượng {'↑' if self.sort_by == 'soluong' and self.sort_order == 'asc' else '↓'}", 
                    height=35,
                    font=("Segoe UI", 15, "bold"),
                    corner_radius=6,
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray80", "gray30"),
                    command=self.toggle_soluong_sort
                )
                self.soluong_sort_btn.grid(row=0, column=col, padx=5, pady=8, sticky="ew")
            elif col == 4:  # Price sort button
                self.price_sort_btn = ctk.CTkButton(
                    header, 
                    text=f"Giá {'↑' if self.sort_by == 'price' and self.sort_order == 'asc' else '↓'}", 
                    height=35,
                    corner_radius=6,
                    font=("Segoe UI", 15, "bold"),
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray80", "gray30"),
                    command=self.toggle_price_sort
                )
                self.price_sort_btn.grid(row=0, column=col, padx=5, pady=8, sticky="ew")
            else:
                label = ctk.CTkLabel(
                    header, 
                    text=text, 
                    font=("Segoe UI", 15, "bold"),
                    anchor="center"
                )
                label.grid(row=0, column=col, padx=5, pady=8, sticky="ew")

    def update_sort_icons(self):
        """Update sort button icons based on current sort state"""
        if hasattr(self, 'price_sort_btn'):
            price_icon = "↑" if self.sort_by == "price" and self.sort_order == "asc" else "↓"
            self.price_sort_btn.configure(text=f"Giá {price_icon}")
        
        if hasattr(self, 'soluong_sort_btn'):
            soluong_icon = "↑" if self.sort_by == "soluong" and self.sort_order == "asc" else "↓"
            self.soluong_sort_btn.configure(text=f"Số lượng {soluong_icon}")

    def toggle_price_sort(self):
        self.sort_by = "price"
        self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        self.update_sort_icons()
        self.load_products()

    def toggle_soluong_sort(self):
        self.sort_by = "soluong"
        self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        self.update_sort_icons()
        self.load_products()

    def load_products(self, products=None):
        # Clear existing widgets
        for widget in self.products_frame.winfo_children():
            widget.destroy()

        if products is None:
            products = self.product_manager.list()

        # Apply sorting
        if self.sort_by:
            reverse = self.sort_order == "desc"
            if self.sort_by == "price":
                products.sort(key=lambda p: self.chuyen_doi(p), reverse=reverse)
            elif self.sort_by == "soluong":
                products.sort(key=lambda p: getattr(p, "soluong", 0), reverse=reverse)

        # Create header
        self.create_product_header()

        # Display products
        if not products:
            # Empty state
            empty_frame = ctk.CTkFrame(self.products_frame, height=200, corner_radius=10)
            empty_frame.pack(fill="x", padx=10, pady=20)
            
            ctk.CTkLabel(
                empty_frame, 
                text="🔍\nKhông tìm thấy sản phẩm nào", 
                font=("Segoe UI", 16),
                text_color="gray"
            ).pack(expand=True)
        else:
            for idx, product in enumerate(products):
                self.create_product_row(product, idx)

    def create_product_row(self, product, index):
        bg_color = ("gray95", "gray15") if index % 2 == 0 else ("white", "gray20")
        
        row = ctk.CTkFrame(self.products_frame, corner_radius=8, fg_color=bg_color)
        row.pack(fill="x", padx=(10,0), pady=2)

        for i in range(6):
            row.grid_columnconfigure(i, weight=1, uniform="col")  # Đảm bảo độ rộng đều nhau

        name_label = ctk.CTkLabel(
            row, 
            text=f"{product.name}", 
            font=("Segoe UI", 16, "bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=0, padx=10, pady=12, sticky="nsew")

        desc_text = product.description[:30] + ("..." if len(product.description) > 30 else "")
        desc_label = ctk.CTkLabel(
            row, 
            text=desc_text, 
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200,
            text_color="gray"
        )
        desc_label.grid(row=0, column=1, sticky="nsew", padx=(95,10),pady = 12)

        category_label = ctk.CTkLabel(
            row, 
            text=str(getattr(product, "category", "N/A")), 
            font=("Segoe UI", 14,"bold"),
            anchor="w"
        )
        category_label.grid(row=0, column=2, sticky="nsew", padx=(115,15),pady = 12)

        quantity = getattr(product, "soluong", 0)
        qty_color = "red" if quantity < 5 else "orange" if quantity < 20 else "green"
        qty_label = ctk.CTkLabel(
            row, 
            text=str(quantity), 
            font=("Segoe UI", 15, "bold"),
            text_color=qty_color,
            anchor="w"
        )
        qty_label.grid(row=0, column=3, sticky="nsew", padx=(135,15),pady = 12)

        price_label = ctk.CTkLabel(
            row, 
            text=f"{product.price:}$", 
            font=("Segoe UI", 15, "bold"),
            text_color="#28a745",
            anchor="w"
        )
        price_label.grid(row=0, column=4, sticky="nsew", padx=(130,15),pady = 12)

        # ACTIONS — dùng grid thay vì pack
        action_frame = ctk.CTkFrame(row, fg_color="transparent")
        action_frame.grid(row=0, column=5, padx=10, pady=8, sticky="nsew")

        col = 0
        detail_btn = ctk.CTkButton(
            action_frame, 
            text="Chi Tiết", 
            width=80,
            height=28,
            corner_radius=6,
            fg_color="#17a2b8",
            hover_color="#138496",
            command=lambda p=product: self.show_detail(p)
        )
        detail_btn.grid(row=0, column=col, padx=2)
        col += 1

        if self.role == "admin":
            edit_btn = ctk.CTkButton(
                action_frame, 
                text="Sửa", 
                width=80,
                height=28,
                corner_radius=6,
                fg_color="#ffc107",
                hover_color="#e0a800",
                text_color="black",
                command=lambda i=index: self.edit_product(i)
            )
            edit_btn.grid(row=0, column=col, padx=2)
            col += 1

            delete_btn = ctk.CTkButton(
                action_frame, 
                text="Xóa", 
                width=80,
                height=28,
                corner_radius=6,
                fg_color="#dc3545",
                hover_color="#c82333",
                command=lambda i=index: self.delete_product(i)
            )
            delete_btn.grid(row=0, column=col, padx=2)


    def show_detail(self, product):

        popup = ctk.CTkToplevel(self)
        popup.title("Chi tiết sản phẩm")
        popup.geometry("650x800")
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.winfo_toplevel())
        popup.grab_set()

        # Main container
        main_frame = ctk.CTkFrame(popup, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Product image
        try:
            image_filename = getattr(product, "image", None)
            if image_filename:
                image_path = os.path.abspath(os.path.join("assets", image_filename))
                if os.path.exists(image_path):
                    image = ctk.CTkImage(light_image=Image.open(image_path), size=(250, 250))
                    img_label = ctk.CTkLabel(main_frame, image=image, text="")
                    img_label.pack(pady=(0, 20))
                else:
                    raise FileNotFoundError("Ảnh không tồn tại")
            else:
                raise ValueError("Thiếu tên ảnh")
        except Exception as e:
            print(f"Không thể tải ảnh: {e}")
            placeholder = ctk.CTkFrame(main_frame, width=250, height=250, corner_radius=10)
            placeholder.pack(pady=(0, 20))
            ctk.CTkLabel(
                placeholder,
                text="\nKhông có ảnh",
                font=("Segoe UI", 16),
                text_color="gray"
            ).place(relx=0.5, rely=0.5, anchor="center")


        # Product info
        info_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 10))

        # Product name
        ctk.CTkLabel(
            info_frame, 
            text=product.name, 
            font=("Segoe UI", 22, "bold"),
            anchor="w",
            wraplength=400,
            justify="left"
        ).pack(fill="x", padx=20, pady=(20, 10))

        # Info grid
        details = [
            ("Giá:", f"{product.price:}$"),
            ("Số lượng:", str(getattr(product, 'soluong', 'N/A'))),
            ("Danh mục:", str(getattr(product, 'category', 'N/A'))),
        ]

        for label, value in details:
            detail_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            detail_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(
                detail_frame, 
                text=label, 
                font=("Segoe UI", 12, "bold"),
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                detail_frame, 
                text=value, 
                font=("Segoe UI", 12),
                anchor="e"
            ).pack(side="right")

        # Description
        desc_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        desc_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            desc_frame,
            text="Mô tả:",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        ).pack(anchor="w")

        desc_box = ctk.CTkTextbox(
            desc_frame,
            width=400,
            height=120,
            font=("Segoe UI", 11),
            wrap="word",
            corner_radius=6
        )
        desc_box.insert("1.0", product.description)
        desc_box.configure(state="disabled")
        desc_box.pack(fill="both", expand=False, pady=(5, 0))


        # Close button
        ctk.CTkButton(
            main_frame, 
            text="Đóng", 
            width=100,
            height=35,
            corner_radius=8,
            command=popup.destroy
        ).pack(pady=20)

    def show_add_dialog(self):

        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm sản phẩm mới")
        dialog.geometry("800x700")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Main container
        main_frame = ctk.CTkFrame(dialog, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_frame, 
            text="Thêm sản phẩm mới", 
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))

        # Form fields
        fields = [
            ("Tên sản phẩm *", "name"),
            ("Giá *", "price"),
            ("Mô tả", "description"),
            ("Danh mục", "category"),
            ("Số lượng", "quantity")
        ]

        entries = {}
        for label, key in fields:
            field_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                field_frame, 
                text=label, 
                font=("Segoe UI", 12, "bold"),
                anchor="w"
            ).pack(anchor="w")
            
            entry = ctk.CTkEntry(
                field_frame,
                height=35,
                corner_radius=8,
                placeholder_text=f"Nhập {label.replace(' *', '').lower()}..."
            )
            entry.pack(fill="x", pady=(5, 0))
            entries[key] = entry

        def add_product():
            name = entries["name"].get().strip()
            price = entries["price"].get().strip()
            desc = entries["description"].get().strip()
            category = entries["category"].get().strip()
            soluong = entries["quantity"].get().strip()

            if not name or not price:
                messagebox.showerror("Lỗi", "Tên sản phẩm và giá không được để trống!")
                return

            try:
                price = float(price)
                soluong = int(soluong) if soluong else 1
                
                if price <= 0:
                    raise ValueError("Giá phải lớn hơn 0")
                if soluong < 0:
                    raise ValueError("Số lượng không được âm")
                    
            except ValueError as e:
                messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {str(e)}")
                return

            new_product = Product(
            id=self.product_manager.get_next_id(),
            name=name,
            price=price,
            description=desc,
            category=category or "Chưa phân loại",
            soluong=soluong
        )

            new_product.category = category or "Chưa phân loại"
            new_product.soluong = soluong
            new_product.id = self.product_manager.get_next_id()

            self.product_manager.add(new_product)
            self.load_products()
            dialog.destroy()
            messagebox.showinfo("Thành công", "Đã thêm sản phẩm thành công!")

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(
            button_frame, 
            text="Thêm sản phẩm", 
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#28a745",
            hover_color="#218838",
            command=add_product
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame, 
            text="Hủy", 
            width=100,
            height=40,
            corner_radius=8,
            fg_color="gray",
            hover_color="darkgray",
            command=dialog.destroy
        ).pack(side="right")
    def browse_image(self, label_widget):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")],
            title="Chọn ảnh từ máy"
        )
        if file_path:
            self.selected_image_path = file_path
            label_widget.configure(text=f"Đã chọn: {os.path.basename(file_path)}")

    def select_asset_image(self, filename, label_widget):
        self.selected_image_path = os.path.abspath(os.path.join("assets", filename))
        label_widget.configure(text=f"Đã chọn: {filename}")

    def edit_product(self, index):
        product = self.product_manager.list()[index]
        self.selected_image_path = None  # reset trước mỗi lần sửa

        dialog = ctk.CTkToplevel(self)
        dialog.title("Chỉnh sửa sản phẩm")
        dialog.geometry("700x750")
        dialog.resizable(True, True)

        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="Chỉnh sửa sản phẩm",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))

        fields = [
            ("Tên sản phẩm *", "name", product.name),
            ("Giá *", "price", str(product.price)),
            ("Mô tả", "description", product.description),
            ("Danh mục", "category", getattr(product, 'category', '')),
            ("Số lượng", "quantity", str(getattr(product, 'soluong', 1)))
        ]

        entries = {}
        for label, key, value in fields:
            field_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(field_frame, text=label, font=("Segoe UI", 12, "bold")).pack(anchor="w")
            entry = ctk.CTkEntry(field_frame, height=35, corner_radius=8)
            entry.insert(0, value)
            entry.pack(fill="x", pady=(5, 0))
            entries[key] = entry

        # Image selection
        image_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        image_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(image_frame, text="Chọn ảnh mới (tuỳ chọn):", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        image_label = ctk.CTkLabel(image_frame, text="Không thay đổi ảnh")
        image_label.pack(anchor="w", pady=(5, 0))

        img_select_btn = ctk.CTkButton(
            image_frame,
            text="📁 Chọn từ máy",
            command=lambda: self.browse_image(image_label)
        )
        img_select_btn.pack(side="left", padx=(0, 10), pady=5)

        asset_images = [f for f in os.listdir("assets") if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        asset_dropdown = ctk.CTkOptionMenu(
            image_frame,
            values=asset_images,
            command=lambda img: self.select_asset_image(img, image_label)
        )
        asset_dropdown.set("Chọn từ assets...")
        asset_dropdown.pack(side="left", padx=(0, 10))

        def save_changes():
            name = entries["name"].get().strip()
            price = entries["price"].get().strip()
            desc = entries["description"].get().strip()
            category = entries["category"].get().strip()
            soluong = entries["quantity"].get().strip()

            if not name or not price:
                messagebox.showerror("Lỗi", "Tên sản phẩm và giá không được để trống!")
                return

            try:
                price = float(price)
                soluong = int(soluong) if soluong else 1

                if price <= 0:
                    raise ValueError("Giá phải lớn hơn 0")
                if soluong < 0:
                    raise ValueError("Số lượng không được âm")

            except ValueError as e:
                messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {str(e)}")
                return

            updated_product = Product(
                id=product.id,
                name=name,
                price=price,
                description=desc,
                category=category,
                soluong=soluong
            )

            if self.selected_image_path:
                image_name = os.path.basename(self.selected_image_path)
                target_path = os.path.join("assets", image_name)

                # Nếu ảnh chưa tồn tại trong assets thì copy vào
                if not os.path.exists(target_path):
                    shutil.copy(self.selected_image_path, target_path)
                updated_product.image = image_name

            else:
                    updated_product.image = getattr(product, "image", "")

            self.product_manager.update(index, updated_product)
            self.load_products()
            dialog.destroy()
            messagebox.showinfo("Thành công", "Đã cập nhật sản phẩm thành công!")

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(
            button_frame,
            text="Lưu thay đổi",
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#28a745",
            hover_color="#218838",
            command=save_changes
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="Hủy",
            width=100,
            height=40,
            corner_radius=8,
            fg_color="gray",
            hover_color="darkgray",
            command=dialog.destroy
        ).pack(side="right")


    def delete_product(self, index):
        """Delete product with confirmation"""
        product = self.product_manager.list()[index]
        
        confirm = messagebox.askyesno(
            "Xác nhận xóa", 
            f"Bạn có chắc chắn muốn xóa sản phẩm '{product.name}'?\n\nHành động này không thể hoàn tác."
        )
        
        if confirm:
            self.product_manager.delete(index)
            self.load_products()
            messagebox.showinfo("Thành công", "Đã xóa sản phẩm thành công!")

    def search_products(self):
        """Search products with improved UX"""
        keyword = self.search_entry.get().lower().strip()
        
        if not keyword:
            self.load_products()
            return
            
        all_products = self.product_manager.list()
        filtered = [
            p for p in all_products 
            if (keyword in p.name.lower() or 
                keyword in p.description.lower() or
                keyword in str(getattr(p, 'category', '')).lower())
        ]
        
        self.load_products(filtered)

    def chuyen_doi(self, product):
        """Convert price to sortable integer"""
        try:
            price_str = str(product.price).replace(".", "").replace("$", "").replace(",", "")
            return float(price_str)
        except:
            return 0
