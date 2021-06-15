import socket
import threading

nickname = input("Choose a nickname: ")
if nickname == 'admin':
    password = input("Enter password for admin: ")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # создаем клиентский сокет
client.connect(('127.0.0.1', 55555))

stop_thread = False

def recive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
                next_message = client.recv(1024).decode('utf-8')
                if next_message == 'PASS':
                    client.send(password.encode('utf-8'))
                    if client.recv(1024).decode('utf-8') == 'REFUSE':
                        print("Connection was refused! Wrong password!")
                        stop_thread = True
                elif next_message == 'BAN':
                    print('Connection refused because of ban!')
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break
        message = f'{nickname}: {input("")}'
        if message[len(nickname)+2:].startswith('/'):
            if nickname == 'admin':
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('utf-8'))
                elif message[len(nickname)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('utf-8'))
            else:
                print("Commands can only be executed by admin!")
        else:
            client.send(message.encode('utf-8'))

recive_thread = threading.Thread(target=recive)
recive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()