from collections import deque
import os
import random
import math
import datetime

class File():
    def __init__(self, path):
        self.fd = os.open(path, os.O_RDONLY, 0777)
        self.lines = deque()
        self.block_size = 4096 * 4096
        self.buff = ''

    def readline(self):
        while len(self.lines) == 0:
            tmp = os.read(self.fd, self.block_size)
            if tmp == '': break
            self.buff += tmp

            tmplines = self.buff.split('\n')
            c = len(tmplines)
            self.buff = tmplines.pop()

            if c > 1: self.lines.extend(tmplines)

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

class HashFuns():
    def __init__(self, n, m):
        self.random_consts = []
        self.m = m
        self.a = 0.6180339887
        random.seed(datetime.datetime.now())
        for i in range(n):
            self.random_consts.append(random.random())

    def hash(self, k, i):
        x = k * self.a
        return int(math.floor(self.m * (x - math.floor(x))))

class Trie():
    def __init__(self):
        self.root = self._create_node()

    def add(self, key, path):
        path.sort()
        node = self.root
        index = 0
        while index < len(path):
            word = path[index]
            if not word in node['w']:
                node['w'][word] = self._create_node()

            node = node['w'][word]
            index += 1

        node['s'].append(key)

    def _create_node(self):
        return {'w' : {},
                's': []}

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # j+1 instead of j since previous_row and current_row are one character longer
            # than s2
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]