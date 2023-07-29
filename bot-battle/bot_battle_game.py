import random, string, redis, sys
from colorama import init, Fore
init(autoreset=True)
# Define entities
class Bot:
    def __init__(self, bot_id, name, health, attack_power, wins=0):
        self.bot_id = bot_id
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.wins = wins
    
    def to_dict(self):
        return {
            "name": self.name,
            "health": self.health,
            "attack_power": self.attack_power,
            "wins": self.wins
        }

class Match:
    def __init__(self, match_id, bot_a: Bot, bot_b: Bot, winner: Bot = None):
        self.match_id = match_id
        self.bot_a = bot_a
        self.bot_b = bot_b
        self.winner = winner
    
    def to_dict(self):
        return {
            "bot_a_id": self.bot_a.bot_id,
            "bot_b_id": self.bot_b.bot_id,
            "winner_id": self.winner.bot_id if self.winner else 0
        }

class LeaderboardEntry:
    def __init__(self, bot, wins):
        self.bot = bot
        self.wins = wins

class RedisUtils:
    def __init__(self):
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
        self.redis_client = redis.StrictRedis(host=master_host, port=master_port, db=db)

    def save_bot_to_redis(self, bot: Bot):
        key = self.get_bot_key(bot.bot_id)
        self.redis_client.hmset(key, bot.to_dict())

    def get_bot_from_redis(self, bot_key):
        bot_data = self.redis_client.hgetall(bot_key)
        bot_id = bot_key.decode('utf-8').split(":")[1]
        return Bot(  bot_id
                   , bot_data[b'name'].decode('utf-8')
                   , int(bot_data[b'health'])
                   , int(bot_data[b'attack_power'])
                   , int(bot_data[b'wins']))

    def get_bot_key(self, bot_id):
        return f"bot:{bot_id}"

    def get_all_bot_keys(self):
        return self.redis_client.keys("bot:*")
    
    def get_all_match_keys(self):
        return self.redis_client.keys("match:*")
    
    def reset_leaderboard(self):
        self.redis_client.delete("leaderboard")

    def reset_bots(self):
        bot_keys_to_delete = self.get_all_bot_keys()
        if bot_keys_to_delete:
            self.redis_client.delete(*bot_keys_to_delete)
    
    def reset_matches(self):
        match_keys_to_delete = self.get_all_match_keys()
        if match_keys_to_delete:
            self.redis_client.delete(*match_keys_to_delete)

    def reset_redis(self):
        self.reset_leaderboard()
        self.reset_matches()
        self.reset_bots()
    
    def get_next_match_id(self):
        return self.redis_client.incr("next_match_id")
    
    def save_match_to_redis(self, match: Match):
        key = f"match:{match.match_id}"
        self.redis_client.hmset(key, match.to_dict())

    def update_leaderboard_for_bot(self, bot):
        self.redis_client.zadd("leaderboard", {bot.name: bot.wins})

    def update_leaderboard(self):
        bot_keys = self.get_all_bot_keys()
        for bot_key in bot_keys:
            bot = self.get_bot_from_redis(bot_key.decode("utf-8"))
            self.update_leaderboard(bot)

    def display_leaderboard(self, top = 10, refresh_interval=1):
        while True:
            import os, time
            os.system("cls" if os.name == "nt" else "clear")

            print(f"{Fore.GREEN}Leaderboard top {top}:")
            print(f"{Fore.YELLOW}Rank\t{Fore.YELLOW}Bot Name\t{Fore.YELLOW}Wins")
            leaderboard_data = self.redis_client.zrevrange("leaderboard", 0, -1, withscores=True)
            rank = 1
            for bot_name, wins in leaderboard_data[:top]:
                print(f"{rank}\t{bot_name.decode('utf-8')}\t\t{int(wins)}")
                rank +=1

            time.sleep(refresh_interval)

# Define logic game
class BotBattleGame:
    def __init__(self):
        self.redis_utils = RedisUtils()

    def save_bot(self, bot):
        self.redis_utils.save_bot_to_redis(bot)

    def generate_random_name(self):
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for i in range(4))

    def add_random_bots_with_reset_redis(self, num_bots):
        self.redis_utils.reset_redis()
        self.add_random_bots(num_bots)

    def add_random_bots(self, num_bots):
        for i in range(num_bots):
            bot_id = i + 1
            name = self.generate_random_name()
            health = random.randint(80, 120)
            attack_power = random.randint(10, 20)
            new_bot = Bot(bot_id, name, health, attack_power)
            self.save_bot(new_bot)

    def get_bot_keys(self):
        return self.redis_utils.get_all_bot_keys()
    
    def get_bot(self, bot_key):
        return self.redis_utils.get_bot_from_redis(bot_key)
    
    def get_next_match_id(self):
        return self.redis_utils.get_next_match_id()

    def save_match(self, match):
        self.redis_utils.save_match_to_redis(match)


    def start_match(self):
        bot_keys = self.get_bot_keys()
        if len(bot_keys) < 2:
            print("Not enough bots to start a match.")
            return

        bot_a_key, bot_b_key = random.sample(bot_keys, 2)
        bot_a = self.get_bot(bot_a_key)
        bot_b = self.get_bot(bot_b_key)

        match_id = self.get_next_match_id()
        new_match = Match(match_id, bot_a, bot_b)
        self.save_match(new_match)
        self.simulate_battle(new_match)

    def simulate_battle(self, match):
        print("Start match...")
        bot_a = match.bot_a
        bot_b = match.bot_b
        bot_a_health = bot_a.health
        bot_b_health = bot_b.health
        print(f"'{bot_a.name}' vs '{bot_b.name}'")
        while bot_a_health > 0 and bot_b_health > 0:
            bot_a_health -= bot_b.attack_power
            bot_b_health -= bot_a.attack_power
        print("Combatting...")
        if bot_a_health <= 0:
            match.winner = bot_b
            bot_b.wins += 1
            bot_b.health = bot_b_health
            self.save_bot(bot_b)
            self.update_leaderboard_for_bot(bot_b)
            print(f"'{bot_b.name}' won!!!")
        else:
            match.winner = bot_a
            bot_a.wins += 1
            bot_a.health = bot_a_health
            self.save_bot(bot_a)
            self.update_leaderboard_for_bot(bot_a)
            print(f"'{bot_a.name}' won!!!")
        
        self.save_match(match)
        print(f"Match end...")
        print("=============\n\n")

    def update_leaderboard(self):
        self.redis_utils.update_leaderboard()
    
    def update_leaderboard_for_bot(self, bot):
        self.redis_utils.update_leaderboard_for_bot(bot)

    def display_leaderboard(self, refresh_interval=1):
        self.redis_utils.display_leaderboard(refresh_interval=refresh_interval)