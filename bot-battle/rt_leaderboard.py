from bot_battle_game import *
import time
def main():
    game = BotBattleGame()
    while True:
        game.display_leaderboard()
        time.sleep(1)
if __name__ == "__main__":
    main()