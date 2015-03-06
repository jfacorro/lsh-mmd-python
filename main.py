# main.py
from lsh import Lsh
from trie_tree import TrieTree

def main(argv):
    path = argv[1]
    # solution = TrieTree(path)
    solution = Lsh(path)
    solution.run()
    
    return 0

def target(*args):
  return main, None

if __name__ == '__main__':
  import sys
  main(sys.argv)