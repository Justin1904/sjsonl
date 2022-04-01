# **S**imple-JSONL Dataset for NLP

This repo is a minimal library for working with [JSON Lines](https://jsonlines.org/) datasets for text data.

**Advantages of JSONL format for text datasets**

1. Human-readable
2. Easy to work with (split, chunk, etc., with just text processing tools)
3. Flexible enough to support a wide range of structured data

**Disadvantages of JSONL format for text datasets**

1. If loading into memory all at once, it is relatively inefficient compared to many other I/O optimized formats
2. If loading partially line by line, one loses random-access capabilities across the dataset

**Goal of this library**

 - Keep the human-readability, easy manipulation & flexibility, and also make it **random-accessible with little upfront cost**.

**What this library doesn't achieve**

- This library **does not** improve the throughput to read/process the content of an entire dataset.

Note that this library is written with DL training applications in mind. In those cases, data loading/processing can be delayed as training progresses and can overlap with GPU operations. Therefore, it is beneficial to shoot for minimal upfront cost and delay the I/O and processing cost till later. However, for synchronous data processing workload, this library offers little to no use as bulk-loading all the data still take the same amount (if not slightly more) of time. Though, it may be of some use if the intention is to sample from a decently large dataset.

To this end, this library takes the approach of lazy-loading aided by an index. The index is just an 1-D numpy array stored alongside the data file that needs to be built first. The i-th integer in the index is essentially the byte-level offset of the i-th line in the data file. At dataloading time, the logic roughly translates to the following pseudo-code:

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
- Ease-of-use
  - Make `JSONLDataset` build index by default when there is not one already, so that users don't need to separately build the index
