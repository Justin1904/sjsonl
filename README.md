# **S**imple-JSONL Dataset for NLP

This repo is a minimal library for working with [JSON Lines](https://jsonlines.org/) datasets for text data.

**Advantages of JSONL format for text datasets**

1. Human-readable
2. Easy to load partially

**Disadvantages of JSONL format for text datasets**

1. Inefficient if loading significant amount of data
2. While partial loading is possible, it usually prevents random access which causes trouble for saving & loading dataloader states

To this end, this library takes a middle ground by first creating an index for a given JSONL data file. The index is just an 1-D numpy
uint32 array (assuming there's less than ~4 billion samples, which is usually the case for today's NLP applications). The i-th integer
in the index is essentially the byte-level offset of the i-th line in the data file. At dataloading time, the logic roughly translates
to the following pseudo-code:

```python
# reading the i-th data point
with open(data_file, 'rb') as f:
    f.seek(index[i])
    raw_bytes = f.readline()
    data = json.loads(raw_bytes.decode('utf-8'))
```

Hopefully, building an index can be done relatively cheaply (if you are using extremely large sizes of dataset, this library is not for you).
It just takes reading through the lines of the data file and recording the offsets. This library provides exactly the tools for that.

## JSONL Indexer

This library comes with a simpler indexer. You need to first index your JSONL file to be able to efficiently load data with random access later.

Example usage:

```python
from sjsonl import JSONLIndexer

indexer = JSONLIndexer("~/data/path/to/my/data.jsonl")
indexer.populate_index()
indexer.write_to_disk()  # can take an explicit "path" argument, by default writes to "~/data/path/to/my/data.index.npy"
```

Once you index your data, you are ready to load data with random access.

## JSONL Dataset

The `JSONLDataset` class assumes your index shares path with your data up to the extension, i.e. index file should be found by replacing the
data path's '.jsonl' extension with '.index.npy'. The indexer puts the index file by default at that location. Once this is ensured, you can
load the data

```python
from sjsonl import JSONLDataset

ds = JSONLDataset("~/data/path/to/my/data.jsonl")
len(ds)  # get the length of the dataset
print(f"Random access at O(1) complexity: {ds[10929]}")  # prints the 10929-th data point
```

## Roadmap

This is not supposed to be a heavy-duty dataloader library. And yet, I could think of several possible improvements.

- Indexing speedup
  - Parallel indexing - multiprocessing
- Loading speedup
  - Use a non-stock high-performance JSON parser such as [pysimdjson](https://github.com/TkTech/pysimdjson), which also supports partial parsing
  - Save & load the compressed index. There are some really fast options like [PyFastPFor](https://github.com/searchivarius/PyFastPFor)
