import select
import socket


# MD5_HASH = '202cb962ac59075b964b07152d234b70' # needs to be found!
MD5_HASH = '81dc9bdb52d04dc20036dbd8313ed055'  # 1234
DIGITS = 4
NOT_FOUND_YET = '.' * DIGITS
IP = '0.0.0.0'
PORT = 9999
CHUNK = 1000
messages_to_send = {}
client_sockets = []
client_to_cores = {}


def setup_server():
    server_socket = socket.socket()
    server_socket.bind((IP, PORT))
    server_socket.listen()
    return server_socket


def disconnect_client(client):
    client_sockets.remove(client)
    client.close()


def main():
    start = 0
    found = False
    answer = ''
    data = ''
    msg_to_send = f'{start}.{CHUNK}'
    server_socket = setup_server()
    print("Listening for clients...")
    while not found or len(client_sockets) != 0:
        # using select to create 2 lists:
        # ready_to_read - a list of sockets which sent something
        # ready_to_write - a list of client sockets ready to receive data from the server
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in ready_to_read:
            # handle a new client connecting
            if current_socket is server_socket:
                (client_socket, client_address) = current_socket.accept()
                print(f"New client joined! {client_address}")
                client_sockets.append(client_socket)

            else:
                try:
                    data = current_socket.recv(1024).decode()
                except Exception:
                    client_sockets.remove(current_socket)
                    current_socket.close()

                else:
                    print(data)
                    if not found:
                        if data.startswith('CORES.') and data[6:].isnumeric():
                            client_to_cores[current_socket] = int(data[6:])
                            messages_to_send[current_socket] = f'{MD5_HASH}.{DIGITS}'

                        elif data == '.' * DIGITS:
                            messages_to_send[current_socket] = f'{start}.{CHUNK}'
                            start += CHUNK * client_to_cores[current_socket]

                        elif data.isnumeric():
                            answer = data
                            found = True
                            for sock in client_sockets:
                                messages_to_send[sock] = answer

                    else:
                        if data == 'BYE.':
                            client_sockets.remove(current_socket)
                            disconnect_client(current_socket)

        for current_socket in ready_to_write:
            if current_socket in messages_to_send:
                current_socket.send(messages_to_send[current_socket].encode())
                print(messages_to_send[current_socket])
                messages_to_send.pop(current_socket)

    print(answer)
    server_socket.close()


if __name__ == '__main__':
    main()
