import hashlib
import multiprocessing

DIGITS = 4
CHUNK = 100
MD5_HASH = '81dc9bdb52d04dc20036dbd8313ed055'
CORES = multiprocessing.cpu_count()


def guess_answer(attempts, found, ans):
    for num in attempts:
        if found.value:
            break

        num = str(num).zfill(DIGITS)
        md5_num = hashlib.md5(num.encode()).hexdigest()
        if md5_num == MD5_HASH:
            found.value = True
            ans.value = num.encode()


def main():
    found = multiprocessing.Value('b', False)
    answer = multiprocessing.Array('c', ('.' * DIGITS).encode())
    start = 0

    while not found.value:
        p = []
        for i in range(CORES):
            current_range = list(range(start, start + CHUNK))
            start += CHUNK
            p.append(multiprocessing.Process(target=guess_answer, args=(current_range, found, answer)))
            p[i].start()

        for process in p:
            process.join()

        print(answer.value)
        

if __name__ == '__main__':
    main()
