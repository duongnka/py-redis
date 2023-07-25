from bot_battle_game import *

def main():
    game = BotBattleGame()
    game.display_leaderboard(refresh_interval=5)

if __name__ == "__main__":
    main()