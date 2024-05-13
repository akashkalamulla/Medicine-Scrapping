# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import mysql.connector

class MedexPipeline:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="springstudent",
            password="springstudent",
            database="medex"
        )
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        sql = "INSERT INTO medicines (brand_name, strength, vitamin_info, manufacturer) VALUES (%s, %s, %s, %s)"
        val = (item.get('brand_name', ''), item.get('strength', ''), item.get('vitamin_info', ''), item.get('manufacturer', ''))
        self.cursor.execute(sql, val)
        self.db.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()

class MedicineScraperPipeline:
    def process_item(self, item, spider):
        return item

