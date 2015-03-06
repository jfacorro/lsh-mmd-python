from aux import File, HashFuns, levenshtein
# from pyhashxx import hashxx

class Lsh():
    def __init__(self, path):
        self.path = path
        self.words = {}
        self.sentences = {}
        self.minhash = {}
        self.lsh = {}

        self.word_count = 0
        self.max_line = 10000

        self.hash_fun_count = 50
        self.band_count = 10
        self.bucket_count = None

        self.candidates = set()

    def _is_max_lines(self, line_count):
        return not self.max_line is None and line_count >= self.max_line

    def _report_progress(self, count, mod = 10000, name = ""):
        if count % mod == 0:
            print "Processed {0} {1}".format(count, name)

    def load(self):
        print "Loading file..."
        f = File(self.path)
        line_count = 0
        for sentence in f:
            line_count += 1
            parts = sentence.split(' ')
            sid = parts[0]
            words_set = set()
            words_list = list()
            self.sentences[sid] = (words_set, words_list)
            for word in parts[1:]:
                if not word in self.words:
                    self.word_count += 1
                    self.words[word] = self.word_count
                words_set.add(self.words[word])
                words_list.append(self.words[word])

            self._report_progress(line_count)
            if self._is_max_lines(line_count):
                break

        f.close()

        self.bucket_count = line_count * 10000
        return (self.word_count, len(self.sentences))

    def hash(self, l, m):
        sum = 0
        for x in l: sum += x * x
        return sum % m

    def build_pairs(self, bucket):
        pairs = set()
        count = len(bucket)
        for i in range(count):
            for j in range(i + 1, count):
                pairs.add((bucket[i], bucket[j]))

        return pairs

    def compute_minhash(self):
        print "Computing MinHash..."
        hashfuns = HashFuns(self.hash_fun_count, self.bucket_count)
        hashes = {}
        wcount = 0

        for wid in range(self.word_count):
            wcount += 1
            self._report_progress(wcount, mod = 1000, name = "words")

            for i in range(self.hash_fun_count):
                hashes[i] = hashfuns.hash(wid, i)

            scount = 0
            for sid in self.sentences:
                (wids, _) = self.sentences[sid]
                if wid in wids:
                    for i in range(self.hash_fun_count):
                        key = (i, sid)
                        if not key in self.minhash or hashes[i] < self.minhash[key]:
                            self.minhash[key] = hashes[i]

    def compute_lsh(self):
        print "Computing LSH..."

        item_per_band = self.hash_fun_count / self.band_count
        for b in range(self.band_count):
            start = b  * item_per_band
            end = start + item_per_band
            for sid in self.sentences:
                band_signature = []
                for hi in range(start, end):
                    band_signature.append(self.minhash[(hi, sid)])
                bucket = self.hash(band_signature, self.bucket_count)
                if not bucket in self.lsh:
                    self.lsh[bucket] = set()

                self.lsh[bucket].add(sid)

        for i in self.lsh:
            if len(self.lsh[i]) > 1:
                bucket = self.lsh[i]
                pairs = self.build_pairs(list(bucket))
                for pair in pairs:
                    self.candidates.add(pair)

        # print self.candidates

    def count_distance(self, dist):
        print "Searching {0} pairs for distance {1} or less".format(len(self.candidates), dist)
        count = 0
        for (x, y) in self.candidates:
            (_, sx) = self.sentences[x]
            (_, sy) = self.sentences[y]
            if levenshtein(sx, sy) <= dist:
                count += 1
        return count

    def run(self):
        (words, sentences) = self.load()
        print "Sentences Count: {0}".format(sentences)
        print "Words Count: {0}".format(words)

        self.compute_minhash()
        self.compute_lsh()
        print self.count_distance(1)
