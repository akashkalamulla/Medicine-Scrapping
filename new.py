from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import mysql.connector
from selenium.common.exceptions import TimeoutException

# Set up Chrome webdriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://medex.com.bd/brandspage=1")
driver.maximize_window()

# Initialize lists to store medicine details
medicine_data = []

# Define a function to extract medicine details
def extract_medicine_details(url):
    driver.get(url)
    time.sleep(2)  # Wait for the page to load

    try:
        medicine_name = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.page-heading-1-l.brand'))
        ).text.strip()

        strength = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@title="Generic Name"]'))
        ).text.strip()

        nutrition_info = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@title="Strength"]'))
        ).text.strip()

        manufacturer = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@title="Manufactured by"]'))
        ).text.strip()

        unit_price = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.col-xs-12.packages-wrapper.mt-6'))
        ).text.strip()

        return (medicine_name, strength, nutrition_info, manufacturer, unit_price)

    except TimeoutException as e:
        print(f"TimeoutException while extracting information from {url}: {e}")
        return None

# Loop through pages to scrape data
current_page = 1
while current_page <= 5:  # Set the maximum page number
    print('Scraping page', current_page)

    # Store current scroll position
    scroll_position = driver.execute_script("return window.scrollY;")

    # Find all product links on the page
    product_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.hoverable-block'))
    )

    # Extract the href attribute of each product link
    product_links_urls = [link.get_attribute("href") for link in product_links]

    # Loop through each product link
    for url in product_links_urls:
        medicine_details = extract_medicine_details(url)
        if medicine_details:
            medicine_data.append(medicine_details)

    try:
        # Click on next page button
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ms-block"]/section/div/nav/ul/li[15]/a'))
        )
        next_button.click()
        time.sleep(2)  # Wait for the page to load

        # Scroll back to the previous position
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        
        current_page += 1

    except TimeoutException:
        print("TimeoutException: No more pages to scrape")
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