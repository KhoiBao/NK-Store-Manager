import requests
import json
import os
import random 

def fetch_products_from_api():
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        formatted = []
        for item in data:
            formatted.append({
                "id": item["id"],
                "name": item["title"],
                "price": item["price"],
                "category": item.get("category", "Unknown"),  # ✅ sửa ở đây
                "description": item.get("description", ""), 
                "soluong": item["count"]
            })
        return formatted
    else:
        raise Exception(f"API failed with status: {response.status_code}")

def save_products_to_json(products):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.abspath(os.path.join(base_dir, "..", "..", "data", "products.json"))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    data = fetch_products_from_api()
    save_products_to_json(data)
