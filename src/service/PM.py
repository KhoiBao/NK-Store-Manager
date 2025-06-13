import os
import json
from src.models.products import Product

class ProductManager:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = os.path.abspath(os.path.join(base_dir, "..", "..", "data", "products.json"))
        self.products = []
        self.load()

    def load(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.products = [Product(**item) for item in data]
        except:
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
            
    def get_next_id(self):
        products = self.list()
        if not products:
            return 1
        max_id = max([int(getattr(p, "id", 0)) for p in products])
        return max_id + 1

