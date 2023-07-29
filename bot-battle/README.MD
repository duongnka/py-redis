# HOW TO SETUP Redis Standalone and Redis Sentinel on Ubuntu
We will build a single redis master with 2 redis slaves and 3 sentinels for handling failover
## 1. Install Redis:
	sudo apt-get update
	sudo apt install redis

## 2. Simulate Redis Sentinel on local machine
	sudo apt install redis-sentinel
	
## 3. Prepare Redis master, replicas, sentinel config files.
### 3.1 Create a folder to hold these config files
    sudo mkdir -p /etc/redis-conf 
    cd /etc/redis-conf
	
### 3.2 Create redis master config 
    sudo vim redis-master.conf
    #copy below config and paste		
    port 6379
    bind 127.0.0.1
    daemonize yes
    dir /path/to/redis-master-data
    logfile "redis-master.log"

### 3.3 Create redis replica 1 config
    sudo vim redis-replica-1.conf
    #copy below config and paste	
    port 6380
    bind 127.0.0.1
    daemonize yes
    dir /path/to/redis-replica-1-data
    logfile "redis-replica-1.log"
    replicaof 127.0.0.1 6379

### 3.4 Create redis replica 2 config
    sudo vim redis-replica-2.conf
    #copy below config and paste
    port 6381
    bind 127.0.0.1
    daemonize yes
    dir /path/to/redis-replica-2-data
    logfile "redis-replica-2.log"
    replicaof 127.0.0.1 6379

### 3.5 Create redis sentinel config
    sudo vim redis-sentinel.conf
    #copy below config and paste
    port 26379
    bind 127.0.0.1
    daemonize yes
    logfile "sentinel.log"
    sentinel monitor redis-master 127.0.0.1 6379 2
    sentinel down-after-milliseconds redis-master 5000
    sentinel failover-timeout redis-master 10000

### 3.6 Create redis sentinel 1 config
    sudo vim redis-sentinel-1.conf
    #copy below config and paste
    port 26380
    bind 127.0.0.1
    daemonize yes
    logfile "sentinel1.log"
    sentinel monitor redis-master 127.0.0.1 6379 2
    sentinel down-after-milliseconds redis-master 5000
    sentinel failover-timeout redis-master 10000

### 3.7 Create redis sentinel 2 config
	sudo vim redis-sentinel-2.conf
    #copy below config and paste
    port 26381
    bind 127.0.0.1
    daemonize yes
    logfile "sentinel2.log"
    sentinel monitor redis-master 127.0.0.1 6379 2
    sentinel down-after-milliseconds redis-master 5000
    sentinel failover-timeout redis-master 10000

## 4. Start Redis server for master, replicas and sentinels

    redis-server /etc/redis-conf/redis-master.conf
    redis-server /etc/redis-conf/redis-replica-1.conf
    redis-server /etc/redis-conf/redis-replica-2.conf

    redis-sentinel /etc/redis-conf/redis-sentinel.conf
    redis-sentinel /etc/redis-conf/redis-sentinel-1.conf
    redis-sentinel /etc/redis-conf/redis-sentinel-2.conf

## 5. Monitor log 
    Open in multiple terminals
    # Terminal 1
    tail -f /path/to/redis-master-data/redis-master.log
    # Terminal 2
    tail -f /path/to/redis-replica-1-data/redis-replica-1.log
    # Terminal 3
    tail -f /path/to/redis-replica-2-data/redis-replica-2.log
    # Terminal 4
    tail -f /etc/redis-conf/sentinel.log

## 6. Simulate failover process:
### 6.1 Shutdown master:
		redis-cli -p <master-port> SHUTDOWN
		

