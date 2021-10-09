from collections import namedtuple
import concurrent.futures
from pathlib import Path
from pprint import pprint
import time
from typing import Callable

FileRecord = ("FileRecord", ["artist", "song"])


def timing(function):
    """Timing decorator."""
    def wrapper(*args, **kwargs):
        start = time.time()
        function(*args, **kwargs)
        end = time.time()
        print("time taken:", function.__name__, end - start)
    return wrapper


def count_paths(dirs: list):
    paths = []
    for dir_ in dirs:
        for path in Path(dir_).iterdir():
            paths.append(path)
#     print("path count:", len(paths))


# def get_file_name(path: pathlib.PosixPath) -> list:
# def get_file_name(path: str) -> FileRecord:
def thread_get_file_name(path: str) -> list:
    path = Path(path)
    names = str(path.stem).split("_")
    return names


# def get_file_name(path: pathlib.PosixPath) -> list:
# def get_file_name(path: str) -> FileRecord:
def process_get_file_name(path: str) -> list:
    path = Path(path)
    names = str(path.stem).split("_")
    return names


def thread_count_words(path: str) -> int:
    with open(path, "r") as f:
        try:
            data = f.read()
            return (len(data.split()),)
        except:
            #log the error
            return (None,)


# def process_count_words(path: str) -> int:
def process_count_words(path: str):
    with open(path, "r") as f:
        data = f.read()
        len(data.split())
#         print(len(data.split()), path)
#         return len(data.split())


@timing
def run_processes(files: list, funct):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(funct, task) for task in files}
#         for future in concurrent.futures.as_completed(futures):
#             print(f"The outcome is {future.result()}")


@timing
def run_threads(files: list, funct):
    results = set()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(funct, task) for task in files}
        for future in concurrent.futures.as_completed(futures):
            results.add(tuple(future.result()))
    print(f"The outcome is {results}")


if __name__ == "__main__":
    root_dir = "/Volumes/SILVER256"
    dirs = [f"{root_dir}/data{str(num)}" for num in range(1, 10)]
    pprint(dirs)

#     quit()

#     print("Single Threaded, count paths:")
#     count_paths(dirs)

    print()
    print("Sequential Results:")
    files = list(Path(dirs[0]).iterdir())
#     print("File count:", len(files))
#     print("Example file:", files[0])


    print()
    print("Threaded Results:")
    run_threads(files, thread_get_file_name)
    run_threads(files, thread_count_words)
    
#     print()
#     print("Mulitprocess Results:")
#     run_processes(files, process_get_file_name)
#     run_processes(files, process_count_words)
