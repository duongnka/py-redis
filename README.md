# py-redis
where I apply redis into the application


# Redis cluster Guideline
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