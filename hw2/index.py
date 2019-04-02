#!/usr/bin/python
import re
import nltk
import sys
import getopt
#'''
def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except (getopt.GetoptError, err):
    usage()
    sys.exit(2)
    
for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"
        
if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)
#'''
#-------this file is for object way---------------
from nltk.tokenize import sent_tokenize as senttok
from nltk.tokenize import word_tokenize as wordtok
from nltk.stem import PorterStemmer
from math import sqrt, ceil, floor
import subprocess as sp
import pickle

class Node:
    def __init__(self, i):
        self.idx = i
        self.next = None
        self.skip = None

class Entry:
    def __init__(self, w):
        self.term = w
        self.freq = 0
        self.next = None

flist = sp.check_output('ls ' + input_directory, shell = True) # byte object
flist = flist.decode("utf8").split('\n')[:-1] # list of strings
flist = [int(i) for i in flist]
    
# create (term, id) pairs
ps = PorterStemmer()
voc = []
for j in range(10):

    idx = flist[j]
    with open(input_directory + str(idx)) as f:

        raw = wordtok(f.read())
        for i in raw:

            head = ps.stem(i).casefold()
            if head.isalpha():
                p = (head, idx)
                if p not in voc:
                    voc.append(p)

# sort pair in term -> id order increasingly
voc.sort()

# construct posting list
book = []
for pair in voc:
       
    if not book or pair[0] != book[-1].term: # add an entry into dictionary
        book.append(Entry(pair[0]))
        tail = book[-1]
    
    n = Node(pair[1]) # create a list node
    book[-1].freq += 1 # add document frequency
    tail.next = n
    tail = tail.next
    
# calculate skip pointer
for en in book:
        
    step = ceil(sqrt(en.freq))
    if step < 2: continue
    
    jf = en.next
    idx = 0
    while jf != None:
        
        if idx % step == 0:
            
            jt = jf
            for _ in range(step):
                
                jt = jt.next
                if jt == None: break
            
            jf.skip = jt
         
        jf = jf.next
        idx += 1
    
with open(output_file_dictionary, 'wb') as w:
    
    pickle.dump(book, w)

with open(output_file_postings, 'wb') as w:
    
    pickle.dump(flist, w)
    for i in book: pickle.dump(i.next, w)
 

