from contextlib import contextmanager
import os
from tempfile import TemporaryDirectory


@contextmanager
def in_temp_dir():
    """ Creates a temporary directory as the working directory. On exit, it is removed. """
    with TemporaryDirectory() as tmpdir:
        with in_dir(tmpdir):
            yield tmpdir


@contextmanager
def in_dir(path):
    """ Changes working directory to given path. On exit, restore to original working directory. """
    cwd = os.getcwd()

    try:
        os.chdir(path)
        yield

    finally:
        os.chdir(cwd)
