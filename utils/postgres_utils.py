import psycopg2
from enum import Enum
import random, string, time

class PostgresUtils:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="duongnka", 
            user="postgres", 
            password="Aa123456", 
            host="localhost"
        )
        self.cursor = self.conn.cursor()

    def fetch_data_from_postgres(self, product_id):
        query = f"SELECT * FROM products WHERE id = {product_id}"
        self.cursor.execute(query)
        return self.cursor.fetchone()
    
    def update_product_price(self, product_id, new_price):
        update_query = f"UPDATE products SET price = {new_price} WHERE id = {product_id}"
        self.cursor.execute(update_query)
        self.conn.commit()
    
    def add_new_product(self, name, price, code):
        insert_query = f"INSERT INTO products (name, price, code) VALUES ({name}, {price}, {code})"
        self.cursor.execute(insert_query)
        new_product_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return new_product_id

    def fetch_data_from_postgres(self, product_id):
        query = f"SELECT * FROM products WHERE id = {product_id}"
        self.cursor.execute(query)
        return self.cursor.fetchone()
    
class PostgresMockData:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="duongnka", 
            user="postgres", 
            password="Aa123456", 
            host="localhost"
        )
        self.cursor = self.conn.cursor()

    def generate_random_name():
        prefixes = ["Cool", "Amazing", "Fantastic", "Awesome"]
        suffixes = ["Gadget", "Widget", "Device", "Tool"]
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        return f"{prefix} {suffix}"

    # mock up data

    def generate_random_name(self):
        prefixes = ["Cool", "Amazing", "Fantastic", "Awesome"]
        suffixes = ["Gadget", "Widget", "Device", "Tool"]
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        return f"{prefix} {suffix}"

    def generate_random_price(self):
        return round(random.uniform(10.0, 1000.0), 2)

    def generate_random_code(self, length=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length)) 

    def generate_mock_product_data(self):
        name = self.generate_random_name()
        price = self.generate_random_price()
        code = self.generate_random_code()
        return name, price, code

    def insert_mock_products_batch(self, num_products=100000, batch_size=10000):
        num_batches = (num_products + batch_size - 1) // batch_size
        remaining_products = num_products

        for batch_num in range(num_batches):
            current_batch_size = min(batch_size, remaining_products)
            mock_data = [self.generate_mock_product_data() for _ in range(current_batch_size)]
            insert_query = "INSERT INTO products (name, price, code) VALUES (%s, %s, %s)"
            print(mock_data[0], '...')
            start_time = time.time()
            self.cursor.executemany(insert_query, mock_data)
            self.conn.commit()
            end_time = time.time()
            print(f"Generated and inserted {current_batch_size} mock products in {end_time - start_time:.2f} seconds.")
            print(f"Inserted batch {batch_num + 1} / {num_batches}")

            remaining_products -= current_batch_size
            if remaining_products <= 0:
                break


