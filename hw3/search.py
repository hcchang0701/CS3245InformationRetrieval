#!/usr/bin/python
import re
import nltk
import sys
import getopt

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o file_of_output")

dictionary_file = postings_file = file_of_queries = file_of_output = None
	
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except (getopt.GetoptError, err):
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)
    
#---------------------------------
from dictionary_class import *
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from math import log, sqrt
from numpy import linalg as la
import heapq as hp
import numpy as np
import pickle

def binarySearch(ls, tok):
    
    left = 0
    right = len(ls)-1
    
    while left <= right:
        
        mid = (left + right)//2
        term = ls[mid].getTerm()
        
        if tok < term:
            right = mid-1
        elif tok > term:
            left = mid+1
        else: # term found
            return mid
	
    return -1
   
with open(dictionary_file, 'rb') as f:
    
    entryList = pickle.load(f)
    vocab_size = len(entryList)
    
with open(postings_file, 'rb') as f:
    
    flist = pickle.load(f) # read docIDs
    N = len(flist)
    docVector = {} # store each doc as a weighting vector
    for t in range(len(entryList)):
        
        list_ptr = pickle.load(f)
        while list_ptr:
            
            docVector.setdefault(list_ptr.getDocID(), np.zeros(vocab_size)) # to check
            docVector[list_ptr.getDocID()][t] = 1 + log(list_ptr.getTermFreq()) # wd = (1 + log(tf))
            list_ptr = list_ptr.getSuccessor()
    
    for docid in docVector.keys():
        try: docVector[docid] /= la.norm(docVector[docid])
        except: pass
    
ps = PorterStemmer()
open(file_of_output, 'w').close() # clean file
with open(file_of_queries, 'r') as f:
        
        for q in f:
            
            # preprocessing
            q = q.strip('\n').split(' ')
            q = [ps.stem(i).casefold() for i in q if i.isalpha()]
            #print(str(q))
            
            termList = {} # count tf of query
            for tok in q:
                
                # check whether the term is valid
                idx = binarySearch(entryList, tok)
                if idx == -1:
                    continue
                
                # check whether the term is duplicate
                if tok in termList.keys():
                    termList[tok][1] += 1
                    continue
                
                print(tok)
                termList[idx] = 1
                # use idx to represent the term
                        
            queryVector = np.zeros(vocab_size) # query as a weighting vector
            for key, val in termList.items():
                # wq = (1 + log(tf)) * log(N/df)
                queryVector[key] = (1 + log(val))*(log(N/entryList[key].getDf()))
            
            try: queryVector /= la.norm(queryVector)
            except: pass
            
            heap = []
            for docid in docVector.keys():            
                # calculate cosine similarity
                dot = 0
                for t in termList.keys():
                    dot += queryVector[t] * docVector[docid][t]
                hp.heappush(heap, (-dot, docid))
                
            result = hp.nsmallest(10, heap)
            #print(result)
            with open(file_of_output, 'a') as w:
                for r in result:
                    if r[0] == 0: break
                    w.write(str(r[1])+' ')
                w.write('\n')         
            
            print('==========')
            
            
            
            