import redis, time, threading
from datetime import datetime
from colorama import init, Fore

# Redis connection
redis_host = 'localhost'
redis_port = 6379
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

# Chat Room Names
chat_rooms = ['Chat Room 1', 'Chat Room 2', 'Chat Room 3']
init(autoreset=True)

def handle_messages(room):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(room)

    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"{Fore.GREEN}[{room}] {message['data']}{Fore.RESET}")

def main():
    print("Available chat rooms:")
    for idx, room in enumerate(chat_rooms, start=1):
        print(f"{idx}. {room}")

    room_choice = int(input("Enter the number of the chat room you want to join: "))
    if 1 <= room_choice <= len(chat_rooms):
        selected_room = chat_rooms[room_choice - 1]
        # Start message handling thread
        message_thread = threading.Thread(target=handle_messages, args=(selected_room,), daemon=True)
        message_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Good bye!")

if __name__ == "__main__":
    main()