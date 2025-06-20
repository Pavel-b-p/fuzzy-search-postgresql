import psycopg2
import random
from faker import Faker
import uuid
import os

fake = Faker()

# Списки для генерации реалистичных данных
categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Sports', 'Home', 'Toys']
brands = ['TechCorp', 'StyleBrand', 'FoodMaster', 'ReadMore', 'SportsPro', 'HomeComfort', 'FunToys']

def introduce_typo(text):
    """Генерация различных типов опечаток в тексте"""
    if len(text) < 2: return text
    
    typo_type = random.choice(['swap', 'delete', 'insert', 'replace'])
    pos = random.randint(0, len(text) - 2)
    
    if typo_type == 'swap':
        return text[:pos] + text[pos+1] + text[pos] + text[pos+2:]
    elif typo_type == 'delete':
        return text[:pos] + text[pos+1:]
    elif typo_type == 'insert':
        return text[:pos] + random.choice('abcdefghijklmnopqrstuvwxyz') + text[pos:]
    elif typo_type == 'replace':
        return text[:pos] + random.choice('abcdefghijklmnopqrstuvwxyz') + text[pos+1:]
    
    return text

def generate_product_data(count=10000):
    """Генерация тестовых данных о продуктах"""
    products = []
    for i in range(count):
        name = fake.catch_phrase()
        # Добавляем опечатки в 10% названий
        if random.random() < 0.1: name = introduce_typo(name)
            
        products.append({
            'name': name,
            'description': fake.text(max_nb_chars=200),
            'category': random.choice(categories),
            'brand': random.choice(brands),
            'sku': f"SKU-{uuid.uuid4().hex[:8].upper()}"
        })
    return products

def insert_into_database(products):
    """Вставка сгенерированных данных в базу данных"""
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    
    try:
        with conn.cursor() as cur:
            for product in products:
                cur.execute("""
                    INSERT INTO products (name, description, category, brand, sku)
                    VALUES (%(name)s, %(description)s, %(category)s, %(brand)s, %(sku)s)
                """, product)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    product_data = generate_product_data(90000)
    insert_into_database(product_data)