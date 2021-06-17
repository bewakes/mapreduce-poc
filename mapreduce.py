import sys
import time
from collections import Counter
from typing import List
import multiprocessing as mp

from preprocess import get_suffixes, remove_punctuation, process_word_suffix

DONE = '__DONE__'
bucket_names = [
    'क',
    'ख',
    'ग',
    'घ',
    'ङ',
    'च',
    'छ',
    'ज',
    'झ',
    'ञ',
    'ट',
    'ठ',
    'ड',
    'ढ',
    'ण',
    'त',
    'थ',
    'द',
    'ध',
    'न',
    'प',
    'फ',
    'ब',
    'भ',
    'म',
    'य',
    'र',
    'ल',
    'व',
    'स',
    'श',
    'ष',
    'ह',
    'अ',
    'आ'
    'ई',
    'इ',
    'उ',
    'ऊ',
    'ॠ',
    'ए',
    'ऐ',
    'ओ',
    '*',
]

SUFFIXES = get_suffixes()


class log_time:
    def __init__(self, blockname='BLOCK'):
        self.blockname = blockname

    def __enter__(self, *args, **kwargs):
        self.time = time.time()

    def __exit__(self, *args, **kwargs):
        print(self.blockname, ': ', time.time() - self.time, 'seconds')


def process_word(word: str) -> str:
    word = remove_punctuation(word)
    word_suffixes: List[str] = process_word_suffix(SUFFIXES, word)
    if not word_suffixes:
        return ''
    return word_suffixes[0]


def read_file(fname, buckets):
    with open(fname) as f:
        # The first line is just the url, omit it
        try:
            f.readline()
            words = f.read().split()
        except UnicodeDecodeError:
            print('UNICODE DECODE ERROR')
            return
        for _w in words:
            w = process_word(_w)
            if not w:
                continue
            q = buckets.get(w[0])
            if q:
                q.put(w)
            else:
                buckets['*'].put(w)


def perform_mapping(input_queue, buckets, pid):
    while True:
        fname = input_queue.get()
        if fname == DONE:
            input_queue.put(DONE)
            return
        read_file(fname.strip(), buckets)


def perform_reduce(items):
    c = Counter(items)
    return list(c.items())


def read_until_done(q):
    while True:
        item = q.get()
        if item == DONE:
            return
        yield item


def main():
    # input queue contains filenames from where processes/mappers take the data
    input_queue = mp.Queue()
    # bucket queues are to group the mapper output
    manager = mp.Manager()
    bucket_queues = manager.dict()
    for x in bucket_names:
        bucket_queues[x] = manager.Queue()

    # initialize processes
    processes = []
    pcount = mp.cpu_count()
    print(pcount)

    for i in range(pcount):
        p = mp.Process(target=perform_mapping, args=(input_queue, bucket_queues, i))
        p.start()
        processes.append(p)

    # map filename to queues
    for i, filepath in enumerate(sys.stdin):
        input_queue.put(filepath)
    input_queue.put(DONE)

    print('------------JOINING------------------')
    for p in processes:
        p.join()
    print('------------JOINED------------------')

    # TO indicate end of each bucket
    for k, v in bucket_queues.items():
        v.put(DONE)

    print('REDUCERS')
    # Now the reducers
    with mp.Pool(pcount) as pool:
        items = [list(read_until_done(x)) for x in bucket_queues.values()]
        results = pool.map(perform_reduce, items)
    for result in results:
        for k, cnt in result:
            print(f'{k},{cnt}')


if __name__ == '__main__':
    main()
