from bot_battle_game import *

def main():
    game = BotBattleGame()
    game.display_leaderboard(refresh_interval=3)

if __name__ == "__main__":
    main()