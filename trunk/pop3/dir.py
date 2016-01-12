import uuid
import os
import sys


class Dir:
    @staticmethod
    def make_unique_dir():
        file_dir = None
        while True:
            file_dir = str(uuid.uuid4())
            try:
                os.mkdir(file_dir)
            except OSError:
                sys.stderr.write('Cannot create a dir\n')
                continue
            break
        return file_dir
