import socket
import multiprocessing
import hashlib
# my_socket = socket.socket()
    # my_socket.connect((IP, PORT))
    # md5_hash = my_socket.recv(1024).decode()
    # my_socket.send(str(CORES).encode())

IP = '127.0.0.1'
PORT = 9999
CORES = multiprocessing.cpu_count()


def guess_answer(attempts, md5_hash, digits, found, ans):
    for num in attempts:
        if found.value:
            break

        num = str(num).zfill(digits)
        md5_num = hashlib.md5(num.encode()).hexdigest()
        if md5_num == md5_hash:
            found.value = True
            ans.value = num.encode()


def main():
    sock = socket.socket()
    sock.connect((IP, PORT))
    sock.send(f'CORES.{CORES}'.encode())
    data = sock.recv(1024).decode()
    print(data)
    md5_hash, digits = data.split('.')[0], int(data.split('.')[1])
    found = multiprocessing.Value('b', False)
    answer = multiprocessing.Array('c', ('.' * digits).encode())

    while not found.value():
        data = sock.recv(1024).decode()
        if data.isnumeric():
            break

        start, chunk = int(data.split('.')[0]), int(data.split('.')[1])
        p = []
        for i in range(CORES):
            current_range = list(range(start, start + chunk))
            start += chunk
            p.append(multiprocessing.Process(target=guess_answer, args=(current_range, md5_hash, digits, found, answer)))
            p[i].start()

        for process in p:
            process.join()

        sock.send(answer.value().decode())
        print(answer.value)


if __name__ == '__main__':
    main()