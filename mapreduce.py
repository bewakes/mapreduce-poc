import sys
import time
import collections
import itertools
from operator import itemgetter
from typing import List
import multiprocessing as mp

from preprocess import remove_punctuation, split_sentences, clean_word



class log_time:
    def __init__(self, blockname='BLOCK'):
        self.blockname = blockname

    def __enter__(self, *args, **kwargs):
        self.time = time.time()

    def __exit__(self, *args, **kwargs):
        print(self.blockname, ': ', time.time() - self.time, 'seconds')


class MapReducer:
    # Modified from https://pymotw.com/2/multiprocessing/mapreduce.html
    def __init__(self, mapper, reducer, partitioner, num_workers=None):
        self.mapper = mapper
        self.reducer = reducer
        self.partitioner = partitioner
        self.pool = mp.Pool(num_workers)

    def __call__(self, inputs, chunksize=None):
        map_responses = self.pool.map(self.mapper, inputs, chunksize)
        partitioned_data = self.partitioner(itertools.chain(*map_responses))
        reduced_values = self.pool.map(self.reducer, partitioned_data, chunksize)
        return reduced_values


def partitioner(mapped_values):
    partitioned_data = collections.defaultdict(list)
    for key, value in mapped_values:
        partitioned_data[key].append(value)
    return partitioned_data.items()


def read_file_and_get_bigrams(fname):
    with open(fname) as f:
        try:
            # The first line is just the url, omit it
            f.readline()
            # The second line is title, omit that as well
            f.readline()
            text = f.read().strip()
        except UnicodeDecodeError:
            print('UNICODE DECODE ERROR')
            return []
        sentences = split_sentences(text)
        bigrams = []
        for sent in sentences:
            splitted = sent.split()
            if not splitted:
                continue
            with_start_end = ['<start>', *map(clean_word, splitted), '<end>']
            bigrams.extend(list(zip(with_start_end, with_start_end[1:])))
        return [(x, 1) for x in bigrams]


def reducer(kv):
    big, counts = kv
    return (big, sum(counts))


def write_result(result, fname):
    with open(fname, 'w') as f:
        for (bg1, bg2), v in result:
            f.write(f'{bg1} {bg2} {v}\n')
    print('done!!')


def main_no_parallel():
    # Input is the stream of filepaths from where data is read
    inputs = map(lambda x: x.strip(), sys.stdin)
    mapped = map(read_file_and_get_bigrams, inputs)
    partitioned = partitioner(itertools.chain(*mapped))
    result = list(itertools.chain(reducer(x) for x in partitioned))
    result.sort(key=itemgetter(1), reverse=True)
    write_result(result, 'single_process.out')


def main(n_cpus):
    # Input is the stream of filepaths from where data is read
    inputs = map(lambda x: x.strip(), sys.stdin)
    mapreducer = MapReducer(read_file_and_get_bigrams, reducer, partitioner, num_workers=n_cpus)
    result = mapreducer(inputs)
    result.sort(key=itemgetter(1), reverse=True)
    write_result(result, 'parallel.out')


if __name__ == '__main__':
    print('running...')
    if len(sys.argv) >= 2 and sys.argv[1] == 'p':
        pcount = mp.cpu_count()
        num_processors = min(pcount, int(sys.argv[2])) if len(sys.argv) >= 3 else pcount
        with log_time(f'PARALLEL with {num_processors} cpus'):
            main(num_processors)
    else:
        with log_time('Single process'):
            main_no_parallel()
