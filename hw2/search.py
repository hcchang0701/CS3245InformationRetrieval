#!/usr/bin/python
import re
import nltk
import sys
import getopt

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

dictionary_file = postings_file = file_of_queries = output_file_of_results = None
	
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
from nltk.tokenize import word_tokenize as wordtok
from nltk.stem import PorterStemmer
import pickle
import numpy as np

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
        
def binarySearch(alist, item):
    
    first = 0
    last = len(alist)-1
    found = False
    while first <= last and not found:
        
        midpoint = (first + last)//2
        if alist[midpoint].term == item:
            found = True
        elif item < alist[midpoint].term:
            last = midpoint-1
        else:
            first = midpoint+1
	
    if not found: return -1
    else: return midpoint
    
def realStuff():
    
    try:
        frequency = 0
        # calculate operations in a group
        if opt[-1] == '!':
            #pass ############
            #'''
            opt.pop()
            fetch = res.pop()
            
            #if element on top of the list is tuple (was processed)
            if type(fetch) == type(tuple()):
                
                tpost = fetch[0]
                tfreq = fetch[1]
                return tpost, tfreq
            
            else:
                
                bs = binarySearch(dic, fetch)
                
                if bs == -1: 
                    return None, 0
                else: 
                    tid = bs # indices of operands in dictionary
                
                tfreq = dic[tid].freq # length of posting list of a term
                tloc = pos[tid] # location of the posting list in file
                
                with open(postings_file, 'rb') as rd:
                    rd.seek(tloc)
                    tpost = pickle.load(rd) # get the posting list of specific term
              
            idlist = []
            while tpost:
                idlist.append(tpost.idx)
                tpost = tpost.next
                
            complist = list(set(universe) - set(idlist))
            head = Node(complist[0])
            tail = head
            for ci in range(1, len(complist)):
                tail.next = Node(complist[ci])
                tail = tail.next
            
            return head, len(complist)
            #'''
        else:
            
            r = opt[-1]
            num = len(opt)
            while opt: opt.pop()
            
            tlist, tid, tloc, tpost, tfreq = [], [], [], [], []
            i2 = 0
            for i in range(num + 1): 
                
                fetch = res.pop()
                if type(fetch) == type(tuple()):
                    tpost.append(fetch[0])
                    tfreq.append(fetch[1])
                    i2 += 1
                    continue
                  
                tlist.append(fetch) # operands
                bs = binarySearch(dic, tlist[i-i2])
                
                if bs == -1:
                    tfreq.append(0)
                    tpost.append(None)
                    continue
                else: tid.append(bs) # indices of operands in dictionary
                
                tfreq.append(dic[tid[i-i2]].freq) # length of posting list of a term
                tloc.append(pos[tid[i-i2]]) # location of the posting list in file
                
                with open(postings_file, 'rb') as rd:
                    rd.seek(tloc[i-i2])
                    tpost.append(pickle.load(rd)) # get the posting list of specific term
            
            if r == '&':
                
                if num > 1:
                    tord = np.argsort(tfreq)
                else: 
                    tord = [0, 1]
                
                mergeResult = Node(0)
                for i in range(len(tord)-1):
                    
                    print('Iteration number: ', i)
                    a = tpost[tord[i]]
                    b = tpost[tord[i+1]]
                    ptr = mergeResult
                    
                    while a != None and b != None:
                        
                        if a.idx == b.idx:
                            print(a.idx, b.idx)
                            ptr.next = Node(a.idx)
                            ptr = ptr.next
                            
                            a = a.next
                            b = b.next
                            frequency += 1
                            
                        elif a.idx < b.idx:
                            if a.skip != None and a.skip.idx <= b.idx:
                                while a.skip != None and a.skip.idx <= b.idx:
                                    a = a.skip
                            else: a = a.next
                            
                        else: 
                            if b.skip != None and b.skip.idx <= a.idx:
                                while b.skip != None and b.skip.idx <= a.idx:
                                    b = b.skip
                            else: b = b.next
                            
                    tpost[tord[i+1]] = mergeResult.next
                
                mergeResult = tpost[tord[i+1]] # the answer is here
            #'''OR
            else:
                
                if num > 1:
                    tord = np.argsort(tfreq)
                else: 
                    tord = [0, 1]
                
                mergeResult = Node(0)
                for i in range(len(tord)-1):
                    
                    print('Iteration number: ', i)
                    a = tpost[tord[i]]
                    b = tpost[tord[i+1]]
                    ptr = mergeResult
                    
                    while a != None or b != None:
                        
                        if a == None:
                            print("b:", b.idx)
                            ptr.next = Node(b.idx)
                            b = b.next
                            
                        elif b == None:
                            print("a:", a.idx)
                            ptr.next = Node(a.idx)
                            a = a.next
                            
                        else:
                            print(a.idx, b.idx)
                            if a.idx == b.idx:
                                ptr.next = Node(a.idx)
                                a = a.next
                                b = b.next
                                
                            elif a.idx < b.idx:
                                ptr.next = Node(a.idx)
                                a = a.next
                                
                            else: 
                                ptr.next = Node(b.idx)
                                b = b.next
                                
                        ptr = ptr.next
                        frequency += 1
                            
                    tpost[tord[i+1]] = mergeResult.next
                
                mergeResult = tpost[tord[i+1]] # the answer is here
            #'''        
    
        return mergeResult, frequency
    except:
        return None, 0

# read universal list of docID
pos = []
with open(postings_file, 'rb') as f:
    universe = pickle.load(f)
    while True:
        try: # go through all the posting lists and store their location
            pos.append(f.tell())
            temp = pickle.load(f)
        except EOFError:
            break
        
with open(dictionary_file, 'rb') as f:
    dic = pickle.load(f)

ps = PorterStemmer()
o = {'!' : 1, '&' : 2, '|' : 3}
# left-associative: ), &, |
# right-associative: (, !
with open(file_of_output, 'w') as w:
    
    with open(file_of_queries, 'r') as f:
    
        for q in f:
            
            err = False
            # substitute operators into symbols
            q = re.sub(r'AND', '&', q)
            q = re.sub(r'OR', '|', q)
            q = re.sub(r'NOT', '!', q)
            q = re.sub(r'(\()', r'\1 ', q)
            q = re.sub(r'(\))', r' \1', q)
            q = q.strip('\n').split(' ')
            #print(q)
    
            # convert query from infix to postfix (shunting yard algo)
            out = [] # output stack
            opt = [] # operator stack
            for tok in q:
                
                if tok.isalpha():
                    out.append(ps.stem(tok).casefold()) # normalization
                    
                elif tok in o.keys(): # determine what is the most priority
                    
                    while opt and opt[-1] != '(' and o[opt[-1]] < o[tok]:
                        out.append(opt.pop())
                        
                    if opt and tok == opt[-1] == '!':
                        opt.pop()
                    else: # (and, and) (or, or) (and, not) (or, not) (or, and)
                        opt.append(tok)
                    
                elif tok == '(': 
                    opt.append(tok)
                    
                elif tok == ')':
                    while opt and opt[-1] != '(': 
                        out.append(opt.pop())
                        
                    if not opt: 
                        err = True
                        break
                    elif opt[-1] == '(': 
                        opt.pop()
                        
                else: # unrecognized token
                    err = True
                    break
            
            while opt:
                r = opt.pop()
                if r in ['(', ')']:
                    err = True
                    break
                out.append(r)
            
            if err: # error occurs while parsing query
                w.write('\n')
                continue
    
            print(out)
            
            try:
                # postfix calculation
                res = []
                h1 = None
                fs = 0
                for y in range(len(out)):
                    #print(out[y])
                    if out[y].isalpha():
                        if not opt:
                            res.append(out[y])
                        else:
                            h1, fs = realStuff()
                            res.append((h1, fs))
                            res.append(out[y])
                    else:
                        if not opt:
                            opt.append(out[y])
                        elif out[y] == opt[-1]:
                            opt.append(out[y])
                        else:
                            h1, fs = realStuff()
                            res.append((h1, fs))
                            opt.append(out[y])
    
                if opt: # something left
                    h1, fs = realStuff()
                    res.append((h1, fs))
    
                # write results into file
                if type(res[0]) == type(tuple()): wptr = res[0][0]
                else:
                    print('hi')
                    bs = binarySearch(dic, res[0])
                    if bs == -1: wptr = None
                    else:                
                        with open(postings_file, 'rb') as rd:
                            rd.seek(pos[bs])
                            wptr = pickle.load(rd) # get the posting list of specific term
                    
                while wptr:
                    w.write("%d " % wptr.idx)
                    wptr = wptr.next
                w.write('\n')
                
            except:
                w.write('\n')
            
