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

# Define logic game
class BotBattleGame:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.bots = []
        self.matches = []
        self.leaderboard = []

    def add_bot(self, bot):
        self.bots.append(bot)

    def add_random_bots(self, num_bots):
        for i in range(num_bots):
            bot_id = i + 1
            name = self.generate_random_name()
            health = random.randint(80, 120)
            attack_power = random.randint(10, 20)
            new_bot = Bot(bot_id, name, health, attack_power)
            self.add_bot(new_bot)

            # Save bot data to Redis
            self.save_bot_to_redis(new_bot)

    def generate_random_name(self):
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for i in range(4))

    def save_bot_to_redis(self, bot):
        key = f"bot:{bot.bot_id}"
        self.redis_client.hset(key, "name", bot.name)
        self.redis_client.hset(key, "health", bot.health)
        self.redis_client.hset(key, "attack_power", bot.attack_power)
        self.redis_client.hset(key, "wins", bot.wins)

    def get_bot_from_redis(self, bot_id):
        key = f"bot:{bot_id}"
        bot_data = self.redis_client.hgetall(key)
        return Bot(bot_id, bot_data[b'name'].decode('utf-8'), int(bot_data[b'health']), int(bot_data[b'attack_power']))


    def start_match(self):
        if len(self.bots) < 2:
            print("Not enough bots to start a match.")
            return

        bot_a, bot_b = random.sample(self.bots, 2)
        match_id = len(self.matches) + 1
        new_match = Match(match_id, bot_a, bot_b)
        self.matches.append(new_match)
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
            self.redis_client.zadd("leaderboard", {bot_b.name: bot_b.wins})
        else:
            match.winner = bot_a
            bot_a.wins += 1
            bot_a.health = bot_a_health
            self.redis_client.zadd("leaderboard", {bot_a.name: bot_a.wins})

    def update_leaderboard(self):
        # Create or update the leaderboard in Redis Sorted Set
        for bot in self.bots:
            self.redis_client.zadd("leaderboard", {bot.name: bot.wins})

    def display_leaderboard(self):
        print("Leaderboard:")
        print("Rank\tBot Name\tWins")
        leaderboard_data = self.redis_client.zrevrange("leaderboard", 0, -1, withscores=True)
        rank = 1
        for bot_name, wins in leaderboard_data[:10]:
            print(f"{rank}\t{bot_name.decode('utf-8')}\t\t{int(wins)}")
            rank += 1

def main():
    game = BotBattleGame()

    num_bots = 100 if len(sys.argv) == 1 else int(sys.argv[1])

    game.add_random_bots(num_bots)

    for _ in range(num_bots):
        game.start_match()

    game.display_leaderboard()

if __name__ == "__main__":
    main()