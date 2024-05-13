import requests
import mysql.connector
import threading
from requests.exceptions import ConnectTimeout, ConnectionError
import time
from lxml import html

class DataExtractionError(Exception):
    pass

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

# Scraping function with retry logic
def scrape_page(page_num, data):
    url = f"https://medex.com.bd/brands?page={page_num}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}
    retries = 3
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)  # Adjust timeout as needed
            response.raise_for_status()
            break  # If successful, exit the loop
        except (ConnectTimeout, ConnectionError) as e:
            print(f"Connection error occurred while scraping page {page_num}: {e}")
            time.sleep(1)  # Add a delay before retrying
    else:
        print(f"Failed to scrape page {page_num} after {retries} retries.")
        return

    # Process the response if successful
    tree = html.fromstring(response.content)
    products = tree.xpath("//div[@class='product-box']")
    for product in products:
        medicine = {}
        try:
            brand_name_elem = product.xpath(".//div[@class='col-xs-12 data-row-top']")
            if brand_name_elem:
                medicine['brand_name'] = brand_name_elem[0].text.strip()
            else:
                raise DataExtractionError("Brand name not found")

            strength_elem = product.xpath(".//span[@class='grey-ligten']")
            if strength_elem:
                medicine['strength'] = strength_elem[0].text.strip()
            else:
                raise DataExtractionError("Strength not found")

            vitamin_info_elem = product.xpath(".//div[@class='col-xs-12']")
            if vitamin_info_elem:
                medicine['vitamin_info'] = vitamin_info_elem[0].text.strip()
            else:
                raise DataExtractionError("Vitamin info not found")

            manufacturer_elem = product.xpath(".//span[@class='data-row-company']")
            if manufacturer_elem:
                medicine['manufacturer'] = manufacturer_elem[0].text.strip()
            else:
                raise DataExtractionError("Manufacturer not found")

            data.append(medicine)
        except DataExtractionError as e:
            print(f"Error extracting data: {e}")
            continue

    print(f"Page {page_num} scraped successfully.")

# Worker function for threading
def worker(pages, data):
    for page in pages:
        scrape_page(page, data)

# Number of threads
num_threads = 10

# Create and start threads
threads = []
data = []
for i in range(num_threads):
    pages = range(i + 1, 100, num_threads)
    thread = threading.Thread(target=worker, args=(pages, data))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Insert data into database
for medicine in data:
    sql = "INSERT INTO medicines (brand_name, strength, vitamin_info, manufacturer) VALUES (%s, %s, %s, %s)"
    val = (medicine.get('brand_name', ''), medicine.get('strength', ''), medicine.get('vitamin_info', ''), medicine.get('manufacturer', ''))
    cursor.execute(sql, val)
    db.commit()

# Close database connection
cursor.close()
db.close()
