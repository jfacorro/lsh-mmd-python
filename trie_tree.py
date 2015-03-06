from aux import File, Trie, levenshtein
from pprint import pprint
import pickle

class TrieTree():
    def __init__(self, path):
        self.path = path
        self.words = {}
        self.sentences = {}
        self.trie = Trie()
        self.word_count = 0
        self.max_lines = 10000000

        self.candidates = []
        self.histogram = {}

    def _is_max_lines(self, line_count):
        return not self.max_lines is None and line_count >= self.max_lines

    def report_progress(self, count):
        if count % 10000 == 0:
            print "Processed " + str(count)

    def build_pairs(self, bucket):
        pairs = []
        count = len(bucket)
        for i in range(count):
            for j in range(i + 1, count):
                pairs.append((bucket[i], bucket[j]))

        return pairs

    def load(self):
        print "Loading file..."
        f = File(self.path)
        line_count = 0
        for sentence in f:
            line_count += 1
            parts = sentence.split(' ')
            sid = parts[0]
            self.sentences[sid] = []
            for word in parts[1:]:
                if not word in self.words:
                    self.word_count += 1
                    self.words[word] = self.word_count
                self.sentences[sid].append(self.words[word])
            
            slen = len(self.sentences[sid])
            if not slen in self.histogram:
                self.histogram[slen] = 0
            self.histogram[slen] += 1
            self.trie.add(sid, self.sentences[sid])

            if self._is_max_lines(line_count): break
            self.report_progress(line_count)

        # pprint(self.trie.root)

    def find_candidates(self, node):
        words = node['w']
        ids = node['s']

        for w in words:
            child = words[w]
            ids.extend(child['s'])
            self.find_candidates(child)

        self.candidates.extend(self.build_pairs(ids))

    def count(self, dist):
        count = 0
        for (x, y) in self.candidates:
            sx = self.sentences[x]
            sy = self.sentences[y]
            if levenshtein(sx, sy) <= dist:
                count += 1

        return count

    def run(self):
        self.load()
        # f = open('histogram.pickle', 'w') 
        # pickle.dump(self.histogram, f, pickle.HIGHEST_PROTOCOL)
        # f = open('sentences.pickle', 'w') 
        # pickle.dump(self.sentences, f, pickle.HIGHEST_PROTOCOL)
        print "Finding candidates..."
        self.find_candidates(self.trie.root)
        # pprint(self.candidates)
        print self.count(1)
