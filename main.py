# main.py
from aux import File
from pyhashxx import hashxx

class Data():
    def __init__(self, path):
        self.path = path
        self.words = {}
        self.sentences = {}
        self.minhash = {}

        self.word_count = 0
        self.max_line = 100000
        self.hash_count = 5

    def _is_max_lines(self, line_count):
        return not self.max_line is None and line_count >= self.max_line

    def _should_report_progress(self, line_count):
        return line_count % 10000 == 0

    def load(self):
        print "Loading file..."
        f = File(self.path)
        line_count = 0
        for sentence in f:
            line_count += 1
            parts = sentence.split(' ')
            sid = parts[0]
            self.sentences[sid] = set()
            for word in parts[1:]:
                if not word in self.words:
                    self.word_count += 1
                    self.words[word] = self.word_count
                self.sentences[sid].add(self.words[word])

            if self._should_report_progress(line_count):
                print str(line_count) + " lines"
            if self._is_max_lines(line_count):
                break

        f.close()

        return (self.word_count, len(self.sentences))

    def compute_minhash(self):
        for word in self.words:
            word_id = self.words[word]
            hashes = {}
            for i in range(self.hash_count):
                hashes[i] = hashxx(word, seed = i)

            for sid in self.sentences:
                if word_id in self.sentences[sid]:
                    for i in range(self.hash_count):
                        key = (i, sid)
                        if not key in self.minhash or hashes[i] < self.minhash[key]:
                            self.minhash[key] = hashes[i]

    def lsh(self):
        print "LSH!!!"

def main(argv):
    path = argv[1]
    data = Data(path)

    (words, sentences) = data.load()
    print "Sentences Count: {0}".format(sentences)
    print "Words Count: {0}".format(words)

    data.compute_minhash()

    return 0

def target(*args):
  return main, None

if __name__ == '__main__':
  import sys
  main(sys.argv)
