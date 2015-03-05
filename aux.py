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
        self.root = self._create_node(self)

    def add(self, key, path):
        self._recur_add(self.root, 0, key, path)

    def _recur_add(self, node, index, key, path):
        if index < len(path):
            word = path[index]
            if not word in node['words']:
                node['words'][word] = self._create_node()

            new_node = node['words']
            self._recur_add(new_node, index + 1, key, path)
        else:
            node['sentences'].add(key)

    def _create_node(self):
        return {'words' : {},
                'sentences': []}
