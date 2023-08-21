import sys
sys.path.append('..')
from utils.redis_utils import * 
from utils.postgres_utils import *

redis_client = RedisUtils(RedisType.CLUSTER).redis_client
postges_utils = PostgresUtils()

MAX_CACHE_SIZE = 1000

def fetch_data_from_postgres(product_id):
    postges_utils.fetch_data_from_postgres(product_id)

def get_product_info(product_id):
    cached_data = redis_client.get(f"product:{product_id}")
    if cached_data:
        print("Data found in Redis cache!")
        return cached_data.decode('utf-8')
    
    print("Fetching data from PostgreSQL...")
    data = fetch_data_from_postgres(product_id)

    redis_client.setex(f"product:{product_id}", 3600, str(data))

    if redis_client.dbsize() > MAX_CACHE_SIZE:
        oldest_key = redis_client.execute_command("LINDEX", 'product_keys', -1)
        redis_client.delete(oldest_key)
        redis_client.execute_command("LPOP", "product_keys")
    
    redis_client.rpush("product_keys", f"product:{product_id}")

    return data

def invalidate_product_cache(product_id):
    redis_client.delete(f"product:{product_id}")
    redis_client.lrem("product_keys", 0, f"product:{product_id}")
    print(f"cache for product {product_id} invalidated.")

def add_new_product(name, price, code):
    new_product_id = postges_utils.add_new_product(name, price, code)
    invalidate_product_cache(new_product_id)
    print(f"New product added with ID {new_product_id}.")

    return new_product_id

def update_product_price(product_id, new_price):
    postges_utils.update_product_price(product_id, new_price)
    invalidate_product_cache(product_id)
    print(f"Product {product_id} price updated.")


