import redis
from enum import Enum

class RedisType(Enum):
    STANDALONE = 'Redis Standalone'
    SENTINELS = 'Redis Sentinels'
    CLUSTER = 'Redis Cluster'

class RedisUtils:
    def __init__(self, redis_type = RedisType.STANDALONE):
        if redis_type == RedisType.STANDALONE:
            self.redis_client = redis.Redis(host="localhost", port=6379)

        elif redis_type == RedisType.SENTINELS:
            sentinel_addresses = [
                ('localhost', 26379), 
                ('localhost', 26380),
                ('localhost', 26381),
            ]
            sentinel = redis.sentinel.Sentinel(
                sentinel_addresses,
                socket_timeout=0.1,
            )
            master_host, master_port = sentinel.discover_master('redis-master')
            self.redis_client = redis.StrictRedis(host=master_host, port=master_port, db=0)

        elif redis_type == RedisType.CLUSTER:
            from redis.cluster import RedisCluster as Redis
            self.redis_client = Redis(host="localhost", port=7001)