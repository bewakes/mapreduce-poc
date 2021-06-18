import multiprocessing as mp
from mapreduce import main, main_no_parallel



for i in range(mp.cpu_count()):
    with logtime print(i)