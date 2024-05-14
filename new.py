from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import mysql.connector
from selenium.common.exceptions import NoSuchElementException

# Set up Chrome webdriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://medex.com.bd/brands?page=1")
driver.maximize_window()

# Initialize lists to store medicine details
medicine_data = []

# Loop through pages to scrape data
for i in range(5):
    print('Scraping page', i + 1)

    # Find all product links on the page
    product_links = driver.find_elements(By.CSS_SELECTOR, 'a.hoverable-block')

    # Extract the href attribute of each product link
    product_links_urls = [link.get_attribute("href") for link in product_links]

    # Loop through each product link
    for url in product_links_urls:
        # Navigate to the product page
        driver.get(url)
        time.sleep(2)  # Wait for the page to load

        try:
            # Extract medicine details
            medicine_name = driver.find_element(By.CSS_SELECTOR, 'h1.page-heading-1-l.brand').text.strip()
            strength = driver.find_element(By.XPATH, '//div[@title="Generic Name"]').text.strip()
            nutrition_info = driver.find_element(By.XPATH, '//div[@title="Strength"]').text.strip()
            manufacturer = driver.find_element(By.XPATH, '//div[@title="Manufactured by"]').text.strip()
            unit_price = driver.find_element(By.CSS_SELECTOR, 'div.col-xs-12.packages-wrapper.mt-6').text.strip()
            
            # Append data to list
            medicine_data.append((medicine_name, strength, nutrition_info, manufacturer, unit_price))

        except NoSuchElementException as e:
            print(f"Error extracting information from {url}: {e}")
            continue

    try:
        # Click on next page button
        next_button = driver.find_element(By.XPATH, '//*[@id="ms-block"]/section/div/nav/ul/li[15]/a')
        next_button.click()
        time.sleep(2)  # Wait for the page to load

    except NoSuchElementException:
        print("No more pages to scrape")
        break

# Connect to MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="springstudent",
    password="springstudent",
    database="medexx"
)

# Create cursor
cursor = connection.cursor()

# Create table if not exists
create_table_query = """
CREATE TABLE IF NOT EXISTS medicine_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(255),
    strength VARCHAR(255),
    nutrition_info VARCHAR(255),
    manufacturer VARCHAR(255),
    unit_price VARCHAR(255)
)
"""
cursor.execute(create_table_query)

# Insert data into table
insert_query = "INSERT INTO medicine_data (medicine_name, strength, nutrition_info, manufacturer, unit_price) VALUES (%s, %s, %s, %s, %s)"
cursor.executemany(insert_query, medicine_data)
connection.commit()

# Print number of records inserted
print(f'{len(medicine_data)} records inserted into medicine_data table')

# Close cursor and connection
cursor.close()
connection.close()

# Close the webdriver
driver.quit()
