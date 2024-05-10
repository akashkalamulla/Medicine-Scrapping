import requests
from bs4 import BeautifulSoup
import mysql.connector

# MySQL database connection settings
username = 'springstudent'
password = 'springstudent'
host = 'localhost'
database = 'medex'

# Create a MySQL connection
cnx = mysql.connector.connect(
    user=username,
    password=password,
    host=host,
    database=database
)

# Create a cursor object
cursor = cnx.cursor()

# Create a table to store medicine information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mediciness (
        id INT PRIMARY KEY,
        brand_name VARCHAR(255),
        strength VARCHAR(255),
        vitamin_info VARCHAR(255),
        manufacturer VARCHAR(255)
    )
''')

# Function to scrape medicine information from a page
def scrape_medicine_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    medicines = []
    for medicine in soup.find_all('div', {'class': 'hoverable-block'}):
        brand_name  = medicine.find('a').text.strip()
        strength = medicine.find('img', {'class': 'grey-ligten'}).get('alt')
        vitamin_info = medicine.find('span', {'class': 'col-xs-12'}).text.strip()
        manufacturer = medicine.find('span', {'class': 'data-row-company'}).text.strip()
        
        medicines.append((brand_name, strength,  vitamin_info, manufacturer))
    
    return medicines

# Scrape medicine information from all pages
alphabets = 'abcdefghijklmnopqrstuvwxyz'
for alpha in alphabets:
    url = f'https://medex.com.bd/brands?alpha={alpha}'
    medicines = scrape_medicine_info(url)
    
    # Insert medicine information into the database
    for medicine in medicines:
        cursor.execute('''
            INSERT INTO medicines (name, dosage_form, strength, composition, manufacturer)
            VALUES (%s, %s, %s, %s, %s)
        ''', medicine)
    
    cnx.commit()

# Close the database connection
cnx.close()