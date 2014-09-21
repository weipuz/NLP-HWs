# NLP-hw1:
# Using heap-based DP algorithm given in pseduo-code, applied bi-gram model and good turing smooth.
#https://class.coursera.org/nlp/lecture/32
import sys, codecs, optparse, os
from heapq import *
from math import log10

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

def datafile(name, sep='\t'):
    "Read key,value pairs from file."
    for line in file(name):
        yield line.split(sep)

#entry tuple
def make_entry(word = '', start_pos = 0, log_prob = -1e30, back_pointer = None):#notice the -INF log_prob 
    return (word,start_pos, log_prob, back_pointer)

#output heap
def dump_heap(myheap):
	for item in myheap:
		if item[3] ==  None:
			print 'word=%-6s, start=%-6d, log_prob=%-12f, back_pointer=%-6s' %(item[0].decode('utf-8'),item[1],item[2],item[3])
		else: 
			print 'word=%-6s, start=%-6d, log_prob=%-12f, back_pointer=%-6d' %(item[0].decode('utf-8'),item[1],item[2],item[3])
    	print

#output entry
def dump_entry(entry):
	if entry[3] ==None:
		print 'word=%-6s, start=%-6d, log_prob=%-12f, back_pointer=%-6s' %(entry[0].decode('utf-8'),entry[1],entry[2],entry[3])
	else:
		print 'word=%-6s, start=%-6d, log_prob=%-12f, back_pointer=%-6d' %(entry[0].decode('utf-8'),entry[1],entry[2],entry[3])
	print

def log_prob(prob):
	if prob <= 0:
		return -1e10
	else:
		return log10(prob)/log10(2)

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[]):
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)
            
        self.N = float(sum(self.itervalues()))
        
        self.missingfn = (lambda k, N: 1./N)
    
    def __call__(self, key): 
        if key in self: 
            return self[key]/self.N  
        else: 
            return self.missingfn(key, self.N)

Pw  = Pdist(datafile(opts.counts1w))
