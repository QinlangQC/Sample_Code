import subprocess, sys
from subprocess import Popen, PIPE, STDOUT

'''
    Perceptron algorithm implementation on data in 'tag_train.dat'.
'''

def read_sentence(lines):
    "Read in sentences"
    sentences = []
    sentence = ""
    for line in lines:
        if line == "\n":
            sentences.append(sentence);
            sentence = ""
        else:
            sentence += line
    return sentences

def process(args):
  "Create a 'server' to send commands to."
  return subprocess.Popen(args, stdin=PIPE, stdout=PIPE)

def call(process, stdin):
  "Send command to a server and get stdout."
  output = process.stdin.write(stdin + "\n\n")
  line = ""
  while 1:
      l = process.stdout.readline()
      if not l.strip(): break
      line += l
  process.stdout.close()
  process.stdin.close()
  return line

def gold_generator(sentence):
    gold_server = process(["python", "tagger_history_generator.py",  "GOLD"])
    return call(gold_server, sentence)

def enum_generator(sentence):
    enum_server = process(["python", "tagger_history_generator.py",  "ENUM"])
    return call(enum_server, sentence)

def decoder(score):
    decode_server = process(['python', 'tagger_decoder.py', 'HISTORY'])
    return call(decode_server, score)

def process_sentence(sentence, words, vectors):
    "Process single sentence"
    gold = gold_generator(sentence)
    enum = enum_generator(sentence)
    output = decoder(score(enum, words, vectors))
    gold_tag = []
    out_tag = []
    lines = gold.split('\n')
    for line in lines:
        if line.find("pydev debugge") != -1 or line == "" or line == '\r' or line.find('STOP') != -1:
            continue
        gold_tag.append(line)
    lines = output.split('\n')
    for line in lines:
        if line.find("pydev debugge") != -1 or line == "" or line == '\r' or line.find('STOP') != -1:
            continue
        out_tag.append(line)
    return gold_tag, out_tag

def score(history, words, vectors):
    "Score a history"
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
        word = words[int(strs[0]) - 1]
        if "SUFF:" + word[len(word) - 3:] + ":3:" + strs[2] in vectors:
            score1 = vectors["SUFF:" + word[len(word) - 3:] + ":3:" + strs[2]]
        if "SUFF:" + word[len(word) - 2:] + ":2:" + strs[2] in vectors:
            score2 = vectors["SUFF:" + word[len(word) - 2:] + ":2:" + strs[2]]
        if "SUFF:" + word[len(word) - 1:] + ":1:" + strs[2] in vectors:
            score3 = vectors["SUFF:" + word[len(word) - 1:] + ":1:" + strs[2]]
        score = score1 + score2 + score3
        line += " " + str(score)
        result += line + '\n'
    #print result
    return result

def update_vector(gold, out, words, vectors):
    "Update feature vector"
    for i in range(len(gold) - 1):
        g = gold[i]
        o = out[i]
        strs = g.split()
        strss = o.split()
        word = words[int(strs[0]) - 1]
        g_tag = strs[2]
        o_tag = strss[2]
        if g_tag == o_tag:
            continue
        f1g = "SUFF:" + word[len(word) - 1:] + ":1:" + g_tag
        f2g = "SUFF:" + word[len(word) - 2:] + ":2:" + g_tag
        f3g = "SUFF:" + word[len(word) - 3:] + ":3:" + g_tag
        f1o = "SUFF:" + word[len(word) - 1:] + ":1:" + o_tag
        f2o = "SUFF:" + word[len(word) - 2:] + ":2:" + o_tag
        f3o = "SUFF:" + word[len(word) - 3:] + ":3:" + o_tag
        if f1g not in vectors:
            vectors[f1g] = 1
        else:
            vectors[f1g] += 1
        if f2g not in vectors:
            vectors[f2g] = 1
        else:
            vectors[f2g] += 1
        if f3g not in vectors:
            vectors[f3g] = 1
        else:
            vectors[f3g] += 1
        if f1o not in vectors:
            vectors[f1o] = -1
        else:
            vectors[f1o] -= 1
        if f2o not in vectors:
            vectors[f2o] = -1
        else:
            vectors[f2o] -= 1
        if f3o not in vectors:
            vectors[f3o] = -1
        else:
            vectors[f3o] -= 1

def main():
    sentences = read_sentence(open("tag_train.dat").readlines())
    vectors = {}
    for t in range(5): # 5 rounds
        i = 0
        for sentence in sentences:
            i += 1
            sys.stderr.write("iteration %s sentence %d...\n" % (str(t + 1), i))
            sentence = sentence.rstrip()
            lines = sentence.split('\n')
            words = []
            for line in lines:
                words.append(line.split('\t')[0])
            gold_tag, out_tag = process_sentence(sentence, words, vectors)
            update_vector(gold_tag, out_tag, words, vectors)

    for v in vectors.keys():
        print "%s %s" % (v, str(vectors[v]))

if __name__ == "__main__":
    main()