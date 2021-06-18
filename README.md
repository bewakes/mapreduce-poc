## Simplel POC of parallel mapreduce
This program creates bigrams from input nepali corpus

### Usage
The input to the program is stream of filepaths.
#### Single threaded use
`find <data_directory> -type f | python mapreduce.py` 
Output in `single_process.out`

#### Multi threaded use
`find <data_directory> -type f | python mapreduce.py p [Optional number of cpus, if not provided uses max cpus available]` 
Output in `parallel.out`
