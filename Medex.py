import requests
from bs4 import BeautifulSoup
import mysql.connector
import time

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="springstudent",
    password="springstudent",
    database="medex"
)
cursor = db.cursor()

# Create table if not exists
cursor.execute("CREATE TABLE IF NOT EXISTS medicines (id INT AUTO_INCREMENT PRIMARY KEY, brand_name VARCHAR(255), strength VARCHAR(255), vitamin_info TEXT, manufacturer VARCHAR(255))")

# Scraping function
def scrape_page(page_num):
    url = f"https://medex.com.bd/brands?page={page_num}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all('div', class_='product-box')
        for product in products:
            brand_name = product.find('div', class_='col-xs-12 data-row-top').text.strip()
            strength = product.find('span', class_='grey-ligten').text.strip()
            vitamin_info = product.find('div', class_='col-xs-12').text.strip()
            manufacturer = product.find('span', class_='data-row-company').text.strip()

            # Insert into database
            sql = "INSERT INTO medicines (brand_name, strength, vitamin_info, manufacturer) VALUES (%s, %s, %s, %s)"
            val = (brand_name, strength, vitamin_info, manufacturer)
            cursor.execute(sql, val)
            db.commit()
        print(f"Page {page_num} scraped successfully.")
    else:
        print(f"Failed to scrape page {page_num}. Status code: {response.status_code}")

# Scraping loop with rate limiting
for page in range(1, 744):
    scrape_page(page)
    time.sleep(1)  # Adjust this value based on the server's tolerance

# Close database connection
cursor.close()
db.close()
