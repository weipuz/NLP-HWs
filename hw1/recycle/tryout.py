import sys, codecs, optparse, os
from heapq import *
import math

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'my_input'), help="input file to segment")
(opts, _) = optparser.parse_args()

def datafile(name, sep='\t'):
    "Read key,value pairs from file."
    for line in file(name):
        yield line.split(sep)

#entry tuple
def make_entry(word = '', start_pos = 0, log_prob = 0, back_pointer = None):
    return (word,start_pos, log_prob, back_pointer)

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[]):
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)

        self.N = float(sum(self.itervalues()))

        self.missingfn = (lambda k, N: math.log( 1./N ) )
    def __call__(self, key):
        if key in self:
            print math.log( self[key]/self.N    )
            return self[key]/self.N
        else:
            print self.missingfn(key, self.N)
            return self.missingfn(key, self.N)

Pw  = Pdist(datafile(opts.counts1w))#load in the probability table.
for item in Pw:
    print item,
    Pw.__call__(item)

print Pw.N
print math.log(1./(Pw.N+1))