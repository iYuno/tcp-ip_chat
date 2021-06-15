import threading
import socket

host = '127.0.0.1' # localhost

port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # создаем серверный сокет
server.bind((host, port)) # привязываем сервер к адресу
server.listen() # переводим сервер для приема подключений

# списки пользователей и их ники
clients = []
nicknames = []


def broadcast(message):
    for client in clients:
        client.send(message) # отпровляем данные в сокет

def handle(client):
    while True:
        try:
            msg = message = client.recv(1024) # принимаем данные из сокета
            if msg.decode('utf-8').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('utf-8')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command was refused!'.encode('utf-8'))
            elif msg.decode('utf-8').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('utf-8')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                        print(f'{name_to_ban} was banned!')
                else:
                    client.send('Command was refused!'.encode('utf-8'))
            else:
                broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close() # закрываем сокет
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        # принимаем соединение и возвращаем новый объект сокета и адрес, привязанный к сокету на другом конце соединения
        client, address = server.accept()
        print(f"connected with {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname+'\n' in bans:
            client.send('BAN'.encode('utf-8'))
            client.close()
            continue

        if nickname == 'admin':
            client.send('PASS'.encode('utf-8'))
            password = client.recv(1024).decode('utf-8')

            if password != 'adminpass':
                client.send('REFUSE'.encode('utf-8'))
                client.close()
                continue

        # добавляем в списки
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
        client.send('Connected to the server!'.encode('utf-8'))

        # запускаем функцию handle в отдельном потоке для конкретного пользователя
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by an admin!'.encode('utf-8'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin!'.encode('utf-8'))

print("Server is listening...")
receive()