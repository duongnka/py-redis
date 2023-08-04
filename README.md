# py-redis
where I apply redis into the application


# Redis Cluster Guideline
Following the below steps to build a redis cluster on mac
## 1. Install Redis with brew
    brew --version
    brew install redis
    # Test installed successfully
    redis-server

## 2. Build Redis-cluster for testing
### 2.1 Preparation
    # Create a cluster with 6 nodes - 3 masters and 3 slaves
    # Create 6 folders representing for 6 nodes 
    mkdir redis-cluster
    cd redis-cluster
    mkdir 7000 7001 7002 7003 7004 7005

In each folder from 7000 to 7005, we create a `redis.conf` file and copy the below config paste into it.

    # Make sure to replace the port number `7000` with the right port
    # number according to the directory name
    port 7000
    cluster-enabled yes
    cluster-config-file nodes.conf
    cluster-node-timeout 5000
    appendonly yes
### 2.2 Build a cluster
Now we can start all these nodes in separate terminal tab

    # Do the same command for other terminal tab, make sure to change 
    # directory name
    cd 7000
    redis-server ./redis.conf

Now we have 6 redis instances running, next we will create a redis cluster by using below command

    redis-cli --cluster create 127.0.0.1:7000 127.0.0.1:7001 \
    127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
    --cluster-replicas 1

Now we have successfully built a redis cluster on mac, you can install RedisInsight - a powerfull Redis GUI - to mornitor the failover and some other stuffs...

Or we can connect to a master node then using the command to show the cluster information

    # Assume port 7001 is a master node
    redis-cli -h localhost -p 7001 
    cluster nodes

# Redis Sentinels Guideline
Make sure you have redis installed on your mac

## 1. Preparation
    mkdir redis-sentinel
    cd redis-sentinel
    mkdir redis-master-data redis-replica1-data redis-replica2-data redis-sentinel-data
Now create redis config file for a master and 2 replicas for this sentinel

### 1.1 Master node
    vim redis-master.conf
    # copy and paste below config
    port 6379
    bind 127.0.0.1
    deamonize yes
    dir redis-master-data
    logfile "redis-master.log"

### 1.2 Replica 1
    vim redis-replica1.conf
    # copy and paste below config
    port 6380
    bind 127.0.0.1
    deamonize yes
    dir redis-replica1-data
    logfile "redis-replica1.log"
    replicaof 127.0.0.1 6379

### 1.3 Replica 2
    vim redis-replica2.conf
    # copy and paste below config
    port 6381
    bind 127.0.0.1
    deamonize yes
    dir redis-replica2-data
    logfile "redis-replica2.log"
    replicaof 127.0.0.1 6379

### 1.4 Configure Redis Sentinel
Create a separate `sentinel1.conf`, `sentinel2.conf`, `sentinel3.conf` file for the Redis Sentinel and configure it as follows:

    # Replace port 26379 for sentinel 1
    # Replace port 26380 for sentinel 2
    # Replace port 26381 for sentinel 3
    port 26379
    sentinel bind 127.0.0.1
    dir redis-sentinel-data
    logfile "redis-sentinel.log"
    sentinel monitor redis-master 127.0.0.1 6379 2

## 2. Start instances
Run follow commands to start Master, Replica 1 and Replica 2 instances

    redis-server redis-master.conf
    redis-server redis-replica1.conf
    redis-server redis-replica2.conf

Now we start 3 sentinel instances, run following comands

    redis-sentinel sentinel1.conf
    redis-sentinel sentinel2.conf
    redis-sentinel sentinel3.conf

Now you successfully create a Redis Sentinel with 3 nodes - one Master and two Replicas - and 3 Sentinel instances to monitor the Master node and handle failover.