class Product:
    def __init__(self, name, price, description=""):
        self.name = name
        self.price = price
        self.description = description

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "description": self.description
        }

    @staticmethod
    def from_dict(data):
        return Product(data['name'], data['price'], data.get('description', ""))
