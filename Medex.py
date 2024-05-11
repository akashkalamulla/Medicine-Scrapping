import requests
from bs4 import BeautifulSoup
import mysql.connector
import threading
from requests.exceptions import ConnectTimeout, ConnectionError
import time

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword",
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
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='product-box')
    for product in products:
        medicine = {}
        medicine['brand_name'] = product.find('div', class_='col-xs-12 data-row-top').text.strip()
        medicine['strength'] = product.find('span', class_='grey-ligten').text.strip()
        medicine['vitamin_info'] = product.find('div', class_='col-xs-12').text.strip()
        medicine['manufacturer'] = product.find('span', class_='data-row-company').text.strip()
        data.append(medicine)
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
    pages = range(i + 1, 744, num_threads)
    thread = threading.Thread(target=worker, args=(pages, data))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Insert data into database
for medicine in data:
    sql = "INSERT INTO medicines (brand_name, strength, vitamin_info, manufacturer) VALUES (%s, %s, %s, %s)"
    val = (medicine['brand_name'], medicine['strength'], medicine['vitamin_info'], medicine['manufacturer'])
    cursor.execute(sql, val)
    db.commit()

# Close database connection
cursor.close()
db.close()
