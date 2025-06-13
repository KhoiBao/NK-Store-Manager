class Product:
    def __init__(self, id, name, price, category="", description="", soluong=0,image=None):
        self.id = int(id)
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.soluong = soluong
        self.image = image

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "description": self.description,
            "soluong": self.soluong,
            "image": self.image  # ✅ lưu image vào JSON
        }

    @staticmethod
    def from_dict(data):
        return Product(
            id=data.get("id", 0),
            name=data["name"],
            price=data["price"],
            category=data.get("category", ""),
            description=data.get("description", ""),
            soluong=data.get("soluong", 0),
            image=data.get("image", None)  # ✅ đọc image từ JSON
        )

