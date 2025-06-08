import json
import os
from models.products import Product


class ProductManager:
    def __init__(self, filepath = "products.json"):
        self.filepath = filepath
        self.products = []
        self.load()

    def load(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.products = [Product(**item) for item in data]
        except FileNotFoundError:
            self.products = []

    def save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump([p.to_dict() for p in self.products], f, ensure_ascii=False, indent=2)

    def list(self):
        return self.products

    def add(self, product):
        self.products.append(product)
        self.save()

    def update(self, index, product):
        if 0 <= index < len(self.products):
            self.products[index] = product
            self.save()

    def delete(self, index):
        if 0 <= index < len(self.products):
            del self.products[index]
            self.save()
