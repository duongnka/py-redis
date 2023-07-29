import redis, time, threading
from datetime import datetime
from colorama import init, Fore

# Redis connection
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
redis_client = redis.StrictRedis(host=master_host, port=master_port, decode_responses=True)

# Chat Room Names
chat_rooms = ['Chat Room 1', 'Chat Room 2', 'Chat Room 3']
init(autoreset=True)

def handle_messages(room):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(room)

    for message in pubsub.listen():
        if message['type'] == 'message':
            message_splitted = message['data'].split("\n")
            user_info = message_splitted[0]
            content = '\n'.join(message_splitted[1:])
            print(f"{Fore.GREEN}[{room}] {user_info}{Fore.RESET}")
            print(f"{Fore.WHITE}{content}{Fore.RESET}")

def main():
    print("Available chat rooms:")
    for idx, room in enumerate(chat_rooms, start=1):
        print(f"{idx}. {room}")

    room_choice = int(input("Enter the number of the chat room you want to join: "))
    if 1 <= room_choice <= len(chat_rooms):
        selected_room = chat_rooms[room_choice - 1]
        print(f"Welcome to {selected_room}!")
        print(f"Waiting for incomming message...")
        message_thread = threading.Thread(target=handle_messages, args=(selected_room,), daemon=True)
        message_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Good bye!")

if __name__ == "__main__":
    main()