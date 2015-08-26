import subprocess, sys
from subprocess import Popen, PIPE, STDOUT

'''
    Test the tagger with data 'tag_dev.dat'.
'''

class Data:
    "Store test data and trained model"
    def __init__(self):
        self.sentences = [] # test data
        self.features = {} # model

    def read_sentences(self, lines):
        sentence = ""
        for line in lines:
            if line == "\n":
                self.sentences.append(sentence);
                sentence = ""
            else:
                sentence += line

    def read_model(self, lines1, lines2):
        for line in lines1:
            strs = line.rstrip().split()
            self.features[strs[0]] = float(strs[1])
        for line in lines2:
            strs = line.rstrip().split()
            self.features[strs[0]] = float(strs[1])

def process(data):
    "Testing"
    for sentence in data.sentences:
        words = sentence.split('\n')
        # Enumerate all possible histories
        p = Popen(['python', 'tagger_history_generator.py', 'ENUM'], stdout = PIPE, stdin = PIPE, stderr = STDOUT)
        out = p.communicate(input = sentence)[0]
        #print out
        # Score histories and find the highest
        p1 = Popen(['python', 'tagger_decoder.py', 'HISTORY'], stdout = PIPE, stdin = PIPE, stderr = STDOUT)
        out1 = p1.communicate(input = score(out, words, data))[0]
        #print out1
        lines = out1.split('\n')
        for line in lines:
            if line.find("pydev debugge") != -1 or line == "" or line == '\r' or line.find('STOP') != -1:
                continue
            strs = line.split()
            print words[int(strs[0]) - 1] + '\t' + strs[2]
        sys.stdout.write('\n')

def score(history, words, data):
    "Score histories"
    histories = history.split('\n')
    result = ""
    for line in histories:
        if line.find("pydev debugger:") != -1 or line == "" or line == "\r":
            continue
        line = line.rstrip();
        strs = line.split()
        score1 = 0
        score2 = 0
        score3 = 0
        score4 = 0
        score5 = 0
        word = words[int(strs[0]) - 1]
        if "BIGRAM:" + strs[1] + ":" + strs[2] in data.features:
            score1 = data.features["BIGRAM:" + strs[1] + ":" + strs[2]]
        if "TAG:" +word + ":" + strs[2] in data.features:
            score2 = data.features["TAG:" + word + ":" + strs[2]]
        if "SUFF:" + word[len(word) - 1:] + ":1:" + strs[2] in data.features:
            score3 = data.features["SUFF:" + word[len(word) - 1:] + ":1:" + strs[2]]
        if "SUFF:" + word[len(word) - 2:] + ":2:" + strs[2] in data.features:
            score4 = data.features["SUFF:" + word[len(word) - 2:] + ":2:" + strs[2]]
        if "SUFF:" + word[len(word) - 3:] + ":3:" + strs[2] in data.features:
            score5 = data.features["SUFF:" + word[len(word) - 3:] + ":3:" + strs[2]]
        score = score1 + score2 + score4 + score5 + score3
        line += " " + str(score)
        result += line + '\n'
    #print result
    return result

def main():
    data = Data()
    data.read_sentences(open("tag_dev.dat").readlines())
    data.read_model(open("tag.model").readlines(), open("suffix_tagger.model").readlines())
    process(data)

if __name__ == "__main__":
    main()

