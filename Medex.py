import requests
import pandas as pd
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime

# Connect to the MySQL database
username = 'springstudent'
password = 'springstudent'
host = 'localhost'
database = 'medexx'

db = mysql.connector.connect(
    user=username,
    password=password,
    host=host,
    database=database
)

# Create a cursor object
cursor = db.cursor()

# Create a table to store medicine information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicines (
        id INT PRIMARY KEY AUTO_INCREMENT,
        brand_name VARCHAR(255),
        strength VARCHAR(255),
        vitamin_info VARCHAR(255),
        manufacturer VARCHAR(255),
        date DATE
    )
''')

# Send a GET request to the URL
url = 'https://medex.com.bd/brands?page=2'
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Find all the product elements
products = soup.find_all('div', class_='col-xs-12 col-sm-6 col-lg-4')

# Loop through each product and extract the data
for product in products:
    # Extract the brand name
    brand_name = product.find('div', class_='col-xs-12 data-row-top').text.strip()

    # Extract the strength
    strength = product.find('span', class_='grey-ligten').text.strip()

    # Extract the vitamin information
    vitamin_info = product.find('div', class_='col-xs-12').text.strip()

    # Extract the company name
    manufacturer = product.find('span', class_='data-row-company').text.strip()

    # Insert the data into the MySQL database
    query = "INSERT INTO medicines (brand_name, strength, vitamin_info, manufacturer, date) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (brand_name, strength, vitamin_info, manufacturer, datetime.today()))

# Commit the changes and close the database connection
db.commit()
db.close()