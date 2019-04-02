#!/usr/bin/python
import re
import nltk
import sys
import getopt
#--------------
import string
import math
import operator

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print('building language models...')
    # This is an empty method
    # Pls implement your code in below
    
    # read sentences(training data) from file
    dic = {}
    with open(in_file, encoding="utf-8-sig") as f:
        for i in f:
            item = i.strip('\n').split(' ', 1)
            dic.setdefault(item[0], [])
            dic[item[0]].append(item[1])
    
    lms = {}
    vocab = set()
    for key, val in dic.items():
        # loop over different languages
        mod = {}
        lms[key] = mod
        for sent in val:
            # preprocess sentences 
            sent = re.sub('['+string.punctuation+']', '', sent) # remove punctuation
            sent = re.sub(r'\d+\s*', '', sent) # remove digits and subsequent spaces
            sent = '<'*(n-1) + sent + '>'*(n-1) # padding start and end
            for i in range(len(sent)-n+1):
                # count frequency
                word = sent[i:i+n]
                mod.setdefault(word, 1)
                mod[word] += 1
        # build vocabulary space among models
        vocab.update(set(mod.keys()))
        
    for key, val in lms.items():
        # smooth the vocab into models
        for w in vocab.difference(set(val.keys())):
            lms[key][w] = 1
        
    return lms
    
    
def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    # This is an empty method
    # Pls implement your code in below
    
    with open(in_file, encoding="utf-8-sig") as f:
        data = f.read().split('\n')[:-1]
    
    result = []
    for idx in range(len(data)):
        
        sent = data[idx]
        sent = re.sub('['+string.punctuation+']', '', sent) # remove punctuation
        sent = re.sub(r'\d+\s*', '', sent) # remove digits and subsequent spaces
        sent = '<'*(n-1) + sent + '>'*(n-1) # padding start and end
        
        word = []
        for i in range(len(sent)-n+1):
            # tokenize a sentence
            word.append(sent[i:i+n])
        #print(word)
        
        res_log = {'indonesian': 0, 'malaysian': 0, 'tamil': 0}
        miss = {}
        for k, v in res_log.items():
            
            count = 0 # match count
            dem = sum(LM[k].values())
            for w in word:
                
                if w in LM[k].keys():
                    res_log[k] += math.log(LM[k][w] / dem)
                    count += 1
               
            miss[k] = 1 - count/len(word)
        
        ans = max(res_log.items(), key=operator.itemgetter(1))
        print(ans, 'miss rate:', miss[ans[0]])
        
        # classify as other if half of matches failed
        if miss[ans[0]] >= 0.5: result.append('other ' + data[idx] + '\n')
        else: result.append(ans[0] + ' ' + data[idx] + '\n')
                        
    with open(out_file, 'w', encoding="utf8") as g:
        g.write(''.join(result))

def usage():
    print("usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file")

def eval_ngram():
    # this function is to calculate how much a ngram-entry contributes to the prediction result for each model
    from numpy import array
    from statistics import mean
    for k in LM.keys():
        a = array(list(LM[k].values()))
        print('%s : %.5f' % (k, math.log( mean(a)/sum(a) )))

n = 4 # self-defined
input_file_b = input_file_t = output_file = None

try: 
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except (getopt.GetoptError, err):
    usage(); sys.exit(2)
    
for o, a in opts:
    if o == '-b': 
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
        
if input_file_b == None or input_file_t == None or output_file == None:
    usage(); sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
#eval_ngram()