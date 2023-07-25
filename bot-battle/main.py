import random, string, redis, sys

# Define entities
class Bot:
    def __init__(self, bot_id, name, health, attack_power):
        self.bot_id = bot_id
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.wins = 0

class Match:
    def __init__(self, match_id, bot_a, bot_b):
        self.match_id = match_id
        self.bot_a = bot_a
        self.bot_b = bot_b
        self.winner = None

class LeaderboardEntry:
    def __init__(self, bot, wins):
        self.bot = bot
        self.wins = wins

class RedisUtils:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def save_bot_to_redis(self, bot):
        key = self.get_bot_key(bot.bot_id)
        self.redis_client.hset(key, "name", bot.name)
        self.redis_client.hset(key, "health", bot.health)
        self.redis_client.hset(key, "attack_power", bot.attack_power)
        self.redis_client.hset(key, "wins", bot.wins)

    def get_bot_from_redis(self, bot_key):
        bot_data = self.redis_client.hgetall(bot_key)
        bot_id = bot_key.decode('utf-8').split(":")[1]
        return Bot(  bot_id
                   , bot_data[b'name'].decode('utf-8')
                   , int(bot_data[b'health'])
                   , int(bot_data[b'attack_power']))

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
    
    def save_match_to_redis(self, match):
        key = f"match:{match.match_id}"
        self.redis_client.hset(key, 'bot_a_id', match.bot_a.bot_id)
        self.redis_client.hset(key, 'bot_b_id', match.bot_b.bot_id)
        self.redis_client.hset(key, 'winner_id', match.winner.bot_id if match.winner else 0)

    def update_leaderboard_for_bot(self, bot):
        self.redis_client.zadd("leaderboard", {bot.name: bot.wins})

    def update_leaderboard(self):
        bot_keys = self.get_all_bot_keys()
        for bot_key in bot_keys:
            bot = self.get_bot_from_redis(bot_key.decode("utf-8"))
            self.update_leaderboard(bot)

    def display_leaderboard(self, top = 10):
        print("Leaderboard:")
        print("Rank\tBot Name\tWins")
        leaderboard_data = self.redis_client.zrevrange("leaderboard", 0, -1, withscores=True)
        rank = 1
        for bot_name, wins in leaderboard_data[:top]:
            print(f"{rank}\t{bot_name.decode('utf-8')}\t\t{int(wins)}")
            rank +=1

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
        bot_a = match.bot_a
        bot_b = match.bot_b
        bot_a_health = bot_a.health
        bot_b_health = bot_b.health

        while bot_a_health > 0 and bot_b_health > 0:
            bot_a_health -= bot_b.attack_power
            bot_b_health -= bot_a.attack_power

        if bot_a_health <= 0:
            match.winner = bot_b
            bot_b.wins += 1
            bot_b.health = bot_b_health
            self.save_bot(bot_b)
            self.update_leaderboard_for_bot(bot_b)
        else:
            match.winner = bot_a
            bot_a.wins += 1
            bot_a.health = bot_a_health
            self.save_bot(bot_a)
            self.update_leaderboard_for_bot(bot_a)
        
        self.save_match(match)

    def update_leaderboard(self):
        self.redis_utils.update_leaderboard()
    
    def update_leaderboard_for_bot(self, bot):
        self.redis_utils.update_leaderboard_for_bot(bot)

    def display_leaderboard(self):
        self.redis_utils.display_leaderboard()

def main():
    game = BotBattleGame()

    num_bots = 100 if len(sys.argv) == 1 else int(sys.argv[1])

    game.add_random_bots(num_bots)

    for _ in range(num_bots):
        game.start_match()

    game.display_leaderboard()

if __name__ == "__main__":
    main()