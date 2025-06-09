import customtkinter as ctk
import json
from tkinter import messagebox
from src.service.PM import ProductManager
from src.models.products import Product


class ProductFrame(ctk.CTkFrame):
    def __init__(self, master, controller, role="user"):
        super().__init__(master)
        self.controller = controller
        self.role = role

        self.product_manager = controller.product_manager

        self.build_ui()
        self.load_products()

    def build_ui(self):
        ctk.CTkLabel(self, text="📦 Danh sách Sản phẩm", font=("Segoe UI", 24, "bold")).pack(pady=10)
        # --- Khung tìm kiếm + sort ---
        search_sort_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_sort_frame.pack(pady=5)

        self.search_entry = ctk.CTkEntry(search_sort_frame, placeholder_text="Nhập tên sản phẩm", width=300)
        self.search_entry.pack(side="left", padx=(0, 10))

        search_btn = ctk.CTkButton(search_sort_frame, text="Tìm", command=self.search_products)
        search_btn.pack(side="left")

        sort_asc_btn = ctk.CTkButton(search_sort_frame, text="Giá cao - thấp", command=self.sort_tang)
        sort_asc_btn.pack(side="left", padx=10)

        sort_desc_btn = ctk.CTkButton(search_sort_frame, text="Giá thấp - cao", command=self.sort_giam)
        sort_desc_btn.pack(side="left", padx=10)

        reset_btn = ctk.CTkButton(search_sort_frame, text="Làm mới", command=self.load_products)
        reset_btn.pack(side="left", padx=10)
        self.products_frame = ctk.CTkScrollableFrame(self)
        self.products_frame.pack(fill="both", expand=True, padx=20, pady=10)

        if self.role == "admin":
            ctk.CTkButton(self, text="Thêm sản phẩm", command=self.show_add_dialog).pack(pady=10)
    def load_products(self, products=None):
        for widget in self.products_frame.winfo_children():
            widget.destroy()

        if products is None:
            products = self.product_manager.list()

        for idx, product in enumerate(products):
            item = ctk.CTkFrame(self.products_frame)
            item.pack(fill="x", padx=5, pady=5)

            name_label = ctk.CTkLabel(item, text=f"{product.name}", font=("Segoe UI", 16, "bold"))
            price_label = ctk.CTkLabel(item, text=f"{product.price}", font=("Segoe UI", 14))
            desc_label = ctk.CTkLabel(item, text=f"{product.description}", font=("Segoe UI", 12), text_color="gray")

            name_label.grid(row=0, column=0, sticky="w")
            price_label.grid(row=0, column=1, sticky="e", padx=10)
            desc_label.grid(row=1, column=0, columnspan=4, sticky="w")

            if self.role == "admin":
                edit_btn = ctk.CTkButton(item, text="Sửa", command=lambda i=idx: self.edit_product(i))
                edit_btn.grid(row=0, column=2, padx=5)

                delete_btn = ctk.CTkButton(item, text="Xoá", fg_color="red", command=lambda i=idx: self.delete_product(i))
                delete_btn.grid(row=0, column=3, padx=5)



    def show_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm sản phẩm")
        dialog.geometry("300x300")

        name_entry = ctk.CTkEntry(dialog, placeholder_text="Tên sản phẩm")
        price_entry = ctk.CTkEntry(dialog, placeholder_text="Giá")
        desc_entry = ctk.CTkEntry(dialog, placeholder_text="Mô tả")

        name_entry.pack(pady=10)
        price_entry.pack(pady=10)
        desc_entry.pack(pady=10)

        def add():
            name = name_entry.get().strip()
            price = price_entry.get().strip()
            desc = desc_entry.get().strip()
            if not name or not price:
                return messagebox.showerror("Lỗi", "Tên và giá không được để trống")

            try:
                price = float(price)
            except:
                return messagebox.showerror("Lỗi", "Giá phải là số")

            new_product = Product(name, price, desc)
            self.product_manager.add(new_product)
            self.load_products()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Thêm", command=add).pack(pady=10)

# Delete an object
    def delete_product(self, index):
        confirm = messagebox.askyesno("Xoá sản phẩm", "Bạn có chắc muốn xoá?")
        if confirm:
            self.product_manager.delete(index)
            self.load_products()
#Find an object
    def search_products(self):
        keyword = self.search_entry.get().lower().strip()
        all_products = self.product_manager.list()
        filtered = [p for p in all_products if keyword in p.name.lower()]
        self.load_products(filtered)
#Sỏrt
    def chuyen_doi(self,product):
        try:
            return int(str(product.price).replace(".", "").replace("₫", "").replace(",", ""))
        except:
            return 0
        
    def sort_tang(self):
        sorted_products = sorted(self.product_manager.list(), key = self.chuyen_doi, reverse = True)
        self.load_products(sorted_products)
    def sort_giam(self):
        sorted_products = sorted(self.product_manager.list(), key = self.chuyen_doi)
        self.load_products(sorted_products)
#Edit
    def edit_product(self, index):
        product = self.product_manager.list()[index]
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sửa sản phẩm")
        dialog.geometry("300x300")

        name_entry = ctk.CTkEntry(dialog, placeholder_text="Tên sản phẩm")
        name_entry.insert(0, product.name)
        price_entry = ctk.CTkEntry(dialog, placeholder_text="Giá")
        price_entry.insert(0, str(product.price))
        desc_entry = ctk.CTkEntry(dialog, placeholder_text="Mô tả")
        desc_entry.insert(0, product.description)

        name_entry.pack(pady=10)
        price_entry.pack(pady=10)
        desc_entry.pack(pady=10)

        def save_edit():
            name = name_entry.get().strip()
            price = price_entry.get().strip()
            desc = desc_entry.get().strip()
            if not name or not price:
                messagebox.showerror("Lỗi", "Tên và giá không được để trống")
                return 
            
            new_product = Product(name, price, desc)
            self.product_manager.update(index, new_product)
            self.load_products()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Lưu", command=save_edit).pack(pady=10)