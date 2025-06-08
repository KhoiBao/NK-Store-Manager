from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import json
from products import Product  

url = "https://www.dienmayxanh.com/dien-thoai"
class DmxSeleniumCrawler:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()

    def crawl_products(self):
        self.driver.get(self.url)
        time.sleep(55) 

        products = []
        items = self.driver.find_elements(By.CSS_SELECTOR, '.item')

        for item in items:
            try:
                name = item.find_element(By.CSS_SELECTOR, 'h3').text
                price = item.find_element(By.CSS_SELECTOR, '.price').text
                desc_elem = item.find_elements(By.CSS_SELECTOR, '.utility')
                desc = desc_elem[0].text if desc_elem else "Không có"

                product = Product(name, price, desc)
                products.append(product)

            except Exception as e:
                print(f"Lỗi đọc sản phẩm: {e}")

        self.driver.quit()
        return products

