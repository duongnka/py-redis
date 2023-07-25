from bot_battle_game import *
import time
def main():
    game = BotBattleGame()

    num_bots = 100 if len(sys.argv) == 1 else int(sys.argv[1])

    game.add_random_bots_with_reset_redis(num_bots)

    for _ in range(num_bots):
        game.start_match()
        time.sleep(1)

if __name__ == "__main__":
    main()