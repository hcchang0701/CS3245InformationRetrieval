#!/usr/bin/python
import re
import nltk
import sys
import getopt

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

#----------------------------------------------------
from nltk.tokenize import word_tokenize as wordtok
from nltk.stem import PorterStemmer
from dictionary_class import *
import subprocess as sp
import pickle

#path = "C:/Users/hccha/AppData/Roaming/nltk_data/corpora/reuters/training/"
flist = sp.check_output('ls ' + input_directory, shell = True) # for unix-like os
#flist = sp.check_output('dir "%s" /b' % input_directory, shell = True) # for windows os
flist = flist.decode("utf8").split('\n')[:-1] # decode byte objects into list of strings
flist = [int(i) for i in flist]

print('start scanning all documents...')    
#create (term, id) tuples
ps = PorterStemmer()
vocabTuple = []
num = len(flist)
for i in range(num):
    with open(input_directory + str(flist[i])) as f:
        if i % 500 == 0 and i: print("%d scanned..." % i)
        rawTok = wordtok(f.read()) #rawTok are unprocessed Tokens
        for j in rawTok:
            term = ps.stem(j).casefold()
            if term.isalpha():
                vocabTuple.append((term, flist[i]))

#sort tupel by term and then by id in increasing order
vocabTuple.sort()
vocabTuple.append(('', 0)) # trailing pair
print('done.')

print('start building the dictionary and postings lists...')
# construct dictionary and posting list
entryList = []
postingsList = []
curPost = None # reference to current tuple
prevPost = None # reference to previously same tuple
for i in vocabTuple:
    
    # check out what pair we get
    if i != prevPost: # different pair
        
        if prevPost != None: # add into list
            
            df += 1
            newPost = Posting(prevPost[1], tf)
            
            if curPost == None: # new postings list
                postingsList.append(newPost)
                curPost = postingsList[-1]
            else: # append 
                curPost.setSuccessor(newPost)
                curPost = curPost.getSuccessor()
            
        # if current tuple has a new term but not trailing pair
        if not entryList or i[0] != entryList[-1].getTerm():
            
            if entryList: # set df of previous term
                entryList[-1].setDf(df)
                
            # create an entry in dictionary
            if i[0] != '':
                entryList.append(DictionaryEntry(i[0]))
                curPost = None
                df = 0 # reset df
        
        prevPost = i
        tf = 1 # reset tf
        
    else: # same pair
        tf += 1
        
print('done.')
'''
for i in range(20):
    print(entryList[i].df, entryList[i].term, postingsList[i].getPostingTuple())
#'''

print('start writing files...')        
sys.setrecursionlimit(1000000)
with open(output_file_dictionary, 'wb') as w:
    pickle.dump(entryList, w)

with open(output_file_postings, 'wb') as w:
    pickle.dump(flist[:num], w) 
    #pickle.dump(postingsList, w)
    for i in postingsList:
        pickle.dump(i, w)

print('done.')