# main.py
import os
from collections import deque

class File():
    def __init__(self, path):
        self.fd = os.open(path, os.O_RDONLY, 0777)
        self.lines = deque()
        self.block_size = 1024 * 4096
        self.buff = os.read(self.fd, self.block_size)

    def readline(self):
        if len(self.lines) == 0:
            while len(self.lines) == 0 and self.buff != '':
                self.buff += os.read(self.fd, self.block_size)
                tmplines = self.buff.split('\n')
                c = len(tmplines)
                self.buff = tmplines.pop()

                if c > 1: self.lines += tmplines

        if len(self.lines) != 0:
            return self.lines.popleft()
        else:
            None

    def close(self):
        os.close(self.fd)

    def __iter__(self):
        return self

    def next(self):
        line = self.readline()
        if line is None:
            raise StopIteration
        else:
            return line

def main(argv):
    f = File('test.txt')

    for line in f:
        print line

    f.close()
    return 0

def target(*args):
  return main, None

if __name__ == '__main__':
  import sys
  main(sys.argv)
