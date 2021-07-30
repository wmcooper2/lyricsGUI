# Description
A CLI tool for setting up the Lyrics database.


### Demo
To run a demo, which only uses the functions from search.py, run:  
    `python3 demo.py --demo`  
Then follow the prompts.


### Purpose(s)
To setup a database for a future lyrics search program.
Store artists and song names in SQL database.
Store all 616,000+ songs in a tarball.
Prepare the data for use in a pi-cluster.
To search through the data collection concurrently.

### Important Points
The final program will contain 5 major stages/areas:  
    * Gather    - collect/scrape the data from the internet and save in an easy to use/store format  
        * CLI tool: `scraper.py`  
    * Clean     - normalize/rename/preprocess in preparation for easy use in later stages/areas  
        * CLI tool: `preprocess.py`  
    * Search    - search for grammar patterns/"vocabulary lists"/etc   
    * Metrics   - calculate metrics that require iterating through the entire data set  
    * Recommend - using user profiles and data about the lyrics, recommend other forms of media related to the user's search  

### Naming Conventions
* TarInfo objects names;
    * are case sensitive
    * artist and song name are separated by underscore
    * and the file has the ".txt" suffix (for when it is extracted)
    * example: `Artist_Song Name.txt`

### Operation
1. "Moved to argparse CLI tool description."
2. "Moved to argparse CLI tool description."
3. METRICS
    * Generate metrics as needed.
    * For each different metric;
        * make the function that you need to calculate it
        * add a field in the DB
        * distribute the new code to the cluster nodes
4. "Moved to argparse CLI tool description."
5. RECOMMENDATION

### Testing
* Run `./test` from project dir
* (TODO) Run `./reset` to clear the contents of `support/` 
* The "coverage" 3rd party package does not work for me...I need to read more on it.

### Notes on Database Operations
* Adding fields to DB
    * manually from DB's shell: `ALTER TABLE songs ADD COLUMN englishScore text;`
    * using this CLI tool: `python3 main.py --dbfield englishScore text`
* Delete fields;
    * have to copy data to new table to delete a field...
* Update a single column single record value;
    * manually from DB's shell: `UPDATE songs SET englishScore=99 WHERE artist="Rihanna";`
* Combine tarballs (uncompressed)
    * manually, go to "Lyrics/" and run:
        ```python
        import tarfile
        from pathlib import Path

        with tarfile.open(name="combined.tar", mode="a") as combined:
            for file_ in Path(".").glob("*.txt"):
                combined.add(file_)
        ```
    * then, move "combined.tar" to the project's root dir.

## Speed tests
Conclusions:
1. Loading the tarball once in the beginning and running batches of searches is best.
    * The bulk of the time is spent just loading the tarball.
    * I think Python caches the tarball's contents because lookups performed after its been opened are fast.

### Loading member list from tarball VS. from text file
```python3
# Setup
import tarfile
from timeit import timeit
tar = tarfile.open(constants.UNCOMPRESSED_TESTING, "r") 

# From tarball
from_tar = timeit("tar.getmembers", number=10000, globals=globals())

# From text file
from_text = timeit("load_text", number=10000, globals=globals())

# Results
# Loading from a text file is faster by about 3x
>>> from_text
0.0006425219999073306
>>> from_tar
0.0022693800000297415
>>> (loaded_from_text / loaded_from_tar) * 100
28.31266689134962
```

## Profiling
Using `cProfile`;  
    1. run `python3 setup.py build_ext --inplace`  
    2. `cProfile.run("lyric_search(songs, members)", filename=f"profile_results/lyric_search_{datetime.utcnow()}.stats")`  
    3. results are saved in `profile_results/lyric_search_<timestamp>.stats`  

Using `SnakeViz`;  
    1. use the profile created with cProfile  
    2. run `snakeviz profile_results/<name of profile>`  

Using `line_profiler`;  
    1. mark the function you want to profile with a decorator: `@profile`  
    2. run `kernprof -l -v your_module.py`  
    3. view the results with: `python -m line_profiler your_profile.py.lprof`  
    
Using `pstats`;  
    1. open a python3 shell  
    2. run this;  
        ```python  
            import pstats  
            p = pstats.Stats("<name of profile>")  
            p.print_stats()  
        ```  

Using `memory_profiler`;  
    source; https://pypi.org/project/memory-profiler/  
    1. mark the function you want to profile with a decorator: `@profile`  
    2. run `python3 -m memory_profiler your_module.py`  


General Process;  
    1. Start with cProfile and use the high level view to guide which functions to profile with `line_profiler` or other profilers  
        * run `python3 setup.py build_ext --inplace` to compile  
    2. run this within your code to profile a specific function;  
        * Example, to profile the `lyric_search` function and save in `filename`  

## Errors
```python
>>>(venv) cooper@Coopers-MacBook-Air tarFileLyricSearch % python3 setup.py build_ext --inplace
...running build_ext
...copying build/lib.macosx-10.9-x86_64-3.9/customEnglish/tarFileLyricSearch/search.cpython-39-darwin.so -> customEnglish/tarFileLyricSearch
...error: could not create 'customEnglish/tarFileLyricSearch/search.cpython-39-darwin.so': No such file or directory

# deleting __init__.py in the same directory solved the problem
```
