from aux import File, Trie

class TrieTree():
    def __init__(self, path):
        self.path = path
        self.words = {}
        self.sentences = {}
        self.trie = Trie()

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
            self.trie.add(sid, self.sentences[sid])

        print self.trie