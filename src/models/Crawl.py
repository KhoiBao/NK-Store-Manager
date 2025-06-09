from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import os
import time

class Product:
    def __init__(self, name, price, image_url):
        self.name = name
        self.price = price
        self.image_url = image_url

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "image_url": self.image_url
        }

def crawl_nguyenkim(url, limit=30):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 "
                         "Safari/537.36 Edg/115.0.1901.183")

    edge_driver_path = r"C:\edgedriver\msedgedriver.exe"  # chỉnh đúng đường dẫn EdgeDriver bạn có
    service = Service(edge_driver_path)
    driver = webdriver.Edge(service=service, options=options)

    print(f"Đang tải trang: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.listproduct"))
        )
        time.sleep(2)  # chờ thêm để trang load xong hẳn
    except Exception as e:
        print(f"❌ Lỗi trong quá trình crawl: {e}")
        driver.quit()
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    products = []
    items = soup.select("ul.listproduct > li.item")

    print(f"Tìm thấy {len(items)} sản phẩm")

    for item in items[:limit]:
        name_tag = item.select_one("h3 > a")
        name = name_tag.text.strip() if name_tag else "Không rõ tên"

        price_tag = item.select_one("span.price")
        price_text = price_tag.text.strip() if price_tag else "0"
        try:
            price = int(price_text.replace(".", "").replace("₫", "").strip())
        except:
            price = 0

        img_tag = item.select_one("img")
        image_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""

        products.append(Product(name, price, image_url))

    return products

def save_to_json(products, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in products], f, ensure_ascii=False, indent=2)
    print(f"✅ Đã lưu {len(products)} sản phẩm vào {file_path}")

if __name__ == "__main__":
    url = "https://www.nguyenkim.com/dien-thoai-di-dong/?features_hash=33-5465"
    products = crawl_nguyenkim(url)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.abspath(os.path.join(base_dir, "..", "..", "data", "nguyenkim_products.json"))
    save_to_json(products, json_path)
