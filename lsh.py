from aux import File, HashFuns
# from pyhashxx import hashxx

class Lsh():
    def __init__(self, path):
        self.path = path
        self.words = {}
        self.sentences = {}
        self.minhash = {}
        self.lsh = {}

        self.word_count = 0
        self.max_line = 100000

        self.band_count = 4
        self.hash_fun_count = 10
        self.bucket_count = None

        self.candidates = set()

    def _is_max_lines(self, line_count):
        return not self.max_line is None and line_count >= self.max_line

    def _should_report_progress(self, count):
        return count % 10000 == 0

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

            if self._should_report_progress(line_count):
                print str(line_count) + " lines"
            if self._is_max_lines(line_count):
                break

        f.close()

        self.bucket_count = line_count * 1000
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
        count = 0

        for wid in range(self.word_count):
            count =+ 1
            if self._should_report_progress(count):
                print str(count) + " lines"

            for i in range(self.hash_fun_count):
                hashes[i] = hashfuns.hash(wid, i)

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

    def distance(self, sid1, sid2):
        (_, s1) = self.sentences[sid1]
        (_, s2) = self.sentences[sid2]

        if len(s1) < len(s2):
            return self.distance(sid2, sid1)

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

    def count_distance(self, dist):
        count = 0
        for (x, y) in self.candidates:
            if self.distance(x, y) <= dist:
                count += 1
        return count

    def run(self):
        (words, sentences) = self.load()
        print "Sentences Count: {0}".format(sentences)
        print "Words Count: {0}".format(words)

        self.compute_minhash()
        self.compute_lsh()
        print self.count_distance(1)