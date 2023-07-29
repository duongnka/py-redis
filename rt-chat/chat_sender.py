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

def send_message(room, user_name):

    # Get the current date and time

    # Format the date and time in a beautiful way
    while True:
        message = input(f"{Fore.CYAN}Enter your message for [{room}]: {Fore.RESET}")
        current_datetime = datetime.now().strftime("%A, %d %B %Y %I:%M %p")

        redis_client.publish(room, f"[{current_datetime}-{user_name}]\n{message}")

def join_chat_room(username, room):
    redis_client.sadd(f"users:{room}", username)
    print(f"{username} has joined {room}")

def leave_chat_room(username, room):
    redis_client.srem(f"users:{room}", username)
    print(f"{username} has left {room}")

def main():
    username = input("Enter your username: ")
    print("Available chat rooms:")
    for idx, room in enumerate(chat_rooms, start=1):
        print(f"{idx}. {room}")

    room_choice = int(input("Enter the number of the chat room you want to join: "))
    if 1 <= room_choice <= len(chat_rooms):
        selected_room = chat_rooms[room_choice - 1]
        join_chat_room(username, selected_room)

        # Start message sending loop
        send_thread = threading.Thread(target=send_message, args=(selected_room, username), daemon=True)
        send_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            leave_chat_room(username, selected_room)

if __name__ == "__main__":
    main()