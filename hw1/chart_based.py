#the new version written on 9.15
import sys, codecs, optparse, os
from heapq import *
from math import log10
import re


optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

# Global Variables 
debug_mode = False

# If learnable, every time finish inserting an entry to chart, we add its count by delta in dict
# The delta is not strictly for smoothing, but we are actually learning from the input. 
#(The assumption is the choice made by our bigram model is quite confident.)
learnable = True
delta = 0.28 # learning step

# Since JM_back_off only get 90.15 locally and 86 on server. I decide not to explore further on this.
JM_back_off = False
lam = 0.6 #JM lambda

# If the single word is unseen, P(w) = Pw(word) * Pw(word[-1])
# Need to think through.. Not in use...
considering_last_character = False 


word_max_len = 8

base = 10 # log base

#Here are some secret parameters, we are doing engineering instead of science HAHAHAHA! :p
# penalty for length 1, 2, 3, 4, 5, more than 5
if considering_last_character:
    length_penalty = [4, 3.0, 7.3, 11.7, 17, 25, 40]
elif JM_back_off: #because we decrease the effect, it doesn't have significant increasee
    length_penalty = [1.60, 4.14, 7.89, 11.81, 15.97, 20, 30]
else: #normal back off without considering characters
    length_penalty = [1.66, 4.15, 7.91, 11.80, 16, 24, 30] # without considering the last char, ts:91.37 88.48 on Learderboard
#length_penalty = [1.4, 3.9, 8, 12, 17, 25, 30]  #training set: 90.15 Learnable: 90.35
#length_penalty = [2, 4, 8, 12, 17, 25, 30]  #training set: 90.10
#length_penalty = [3, 3.9, 8.1, 15, 17, 25, 30]

def datafile(name, sep='\t'):
    "Read key,value pairs from file."
    for line in file(name):
        yield line.split(sep)

#output heap
def dump_heap(myheap):
    for item in myheap:
        if item[3] ==  None:
            print 'heap: chartEntry( word=%s, start=%d, end=%d, log_prob=%f, back_pointer=%s )' %(item[0].decode('utf-8'),item[1], item[1]+len(item[0])/3-1, item[2],item[3])
        else: 
            print 'heap: chartEntry( word=%s, start=%d, end=%d, log_prob=%f, back_pointer=%d )' %(item[0].decode('utf-8'),item[1],item[1]+len(item[0])/3-1, item[2],item[3])
        print

#output entry
def dump_entry(entry):
    if entry[3] ==None:
        print 'chartEntry( word=%s, start=%d, end=%d, log_prob=%f, back_pointer=%s )' %(entry[0].decode('utf-8'),entry[1], entry[1]+len(entry[0])/3-1, entry[2],entry[3])
    else:
        print 'chartEntry( word=%s, start=%d, end=%d, log_prob=%f, back_pointer=%d )' %(entry[0].decode('utf-8'),entry[1], entry[1]+len(entry[0])/3-1, entry[2],entry[3])
    print

#return log probability, base is 2 for observer's convenience and other non-trivial stuff..
def log_prob(prob):
    global base
    if prob <= 0:
        return -1e10
    else:
        return log10(prob)/log10(base)


class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[],  missingfn=None):
        self.tail = {}
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)
            word = key.decode('utf-8')
            if len(word) > 1:
                self.tail[ word[-1] ] = self.tail.get(word[-1], 0) + int(count)

        self.tailN = float(sum(self.tail.itervalues()))

        self.N = float(sum(self.itervalues()))
        
        self.missingfn = missingfn or (lambda k, N: 0 )
    
    def __call__(self, key): 
        if key in self: 
            return self[key]/self.N  
        else:     
            return self.missingfn(key, self.N)#I change it to 1/2N here, not really necessary.

    #if the key only contains one character, return its probabilty as the last char.
    def tail_prob(self, key):
        if key in self.tail:
            return self.tail[key]/self.tailN
        else:
            return 1.0/self.tailN


    #learning from input
    def update(self, key, delta):
        if key in self and self[key] > 1:
            self[key] += 1
            self.N += 1
        elif key in self:
            temp = self[key]
            self[key] = self[key]*1.1 + delta
            self.N += self[key] - temp
        else:
            self[key] = self.get(key, 0)  + float(delta)
            self.N += delta
        # print key.decode('utf-8'), self[key]

# original rough model
def avoid_long_words(word, N):
    "Estimate the probability of an unknown word."
    return 10./(N * 10**len(word))

def avoid_long_words_II(word, N):
    global length_penalty, base, considering_last_character
    cword = word.decode('utf-8')
    l = len(word)/3
    if l > 6:
        l = 7
    if considering_last_character:
        if l <= 1:
            return base /float(N * base **length_penalty[l-1])
        else:
            return base*Pw(cword[-1].encode('utf-8'))  /float(N * base **length_penalty[l-1])
    else:
        return base /float(N * base **length_penalty[l-1])

def cPw(word, prev):
    "The conditional probability P(word | previous-word)."
    try:
        return P2w[prev + ' ' + word]/float(Pw[prev])
    except KeyError:
        return Pw(word)  

def JMPw(word, prev):
    global lam
    try: 
        return lam * P2w(prev + ' ' + word)/Pw[prev] + (1-lam)*Pw(word)
    except KeyError:
        return (1-lam)*Pw(word)

#load in the probability table.
#avoid_long_words: if word not found, then the longer the word, the less likely it is right
Pw  = Pdist(datafile(opts.counts1w),  avoid_long_words_II) 
P2w = Pdist(datafile(opts.counts2w) )

#entry tuple
def make_entry(word = '', start_pos = 0, log_prob = -1e10, back_pointer = None):#notice the -INF log_prob 
    return (word,start_pos, log_prob, back_pointer)

#========================== Begin : Word Segmentation =================================
def word_seg(input_line):
    line_len = len(input_line)    
    global word_max_len
    chart = []   
    myheap =  []

    #=========== Trivial Check: If only one character just return it ===============
    if line_len <= 1:
        output_line = []
        output_line.append(input_line[0:].encode('utf-8'))
        return output_line

    #======================= Initialize Candidates Chart  ===========================    
    for i in range(line_len+1):
        chart.append(make_entry())
    chart[0] = make_entry("", 0, 0, None)

    current_word = input_line[0].encode('utf-8')
    logprob = log_prob(cPw(current_word, ""))
    current_entry = make_entry(current_word, 0, logprob, None)
    chart[1] = current_entry
            
    i = 2

    if debug_mode:
        print
        print "="*12,"Initialize Candidates Chart & Heap ", "="*12
        dump_entry(chart[0])
        dump_entry(chart[1])
        print "="*12," Initialization Complete ", "="*12
    #=============================== Initialization Complete ===========================
    while i <= line_len:
        for j in range(word_max_len):
            if j == 0 :
                continue
            if j > i :
                break
           
            current_word = input_line[i-j:i].encode('utf-8')
            previous_word  =  chart[i-j][0]
            global JM_back_off
            if JM_back_off:
                logprob = log_prob(JMPw(current_word, previous_word))
            else: #normal back off, if bigram is not applicable, back off to unigram
                logprob = log_prob(cPw(current_word, previous_word))#the log prob gets lower and lower, and then it will ignore reasonable segment
            entry = make_entry(current_word, i-j, chart[i-j][2] + logprob, i-j)


            if debug_mode:
                dump_entry( entry ) 
                print "%f < %f" % (chart[i][2], chart[i-j][2] +  logprob)

            if chart[i][2] <= chart[i-j][2] +  logprob:
                chart[i] = entry
                if debug_mode:
                    print
                    print "[Chart Updated]: chart[%d]" %i,        
                    dump_entry (chart[i])  
                    print
        i = i+1;

    #build output from chart table and backpointer
    output_line  = []
    entry = chart[line_len]
    output_line.append(entry[0])
    global delta, learnable
    if learnable:
        Pw.update(entry[0], delta)
    while entry[3] is not None and entry[3] != 0:#append all previous words until chart[0]
        output_line.append(chart[entry[3]][0])        
        entry  = chart[entry[3]]
        if learnable:
            Pw.update(entry[0], delta)
    return output_line
   
#========================== End : Word Segmentation =================================

old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

with open(opts.input) as f:
    for line in f:        
        utf8line = unicode(line.strip(), 'utf-8')
        #do some preprocessing to the sentence, break it into pieces by punctuations ,     
        split_line_comma = utf8line.split(u'\uff0c') #split by comma
        # print re.match(ur"[\u4e00-\u9fa5]", utf8line)
        seg_line=''
        for item in split_line_comma:  
            #print item  
            split_line_dunhao=item.split(u'\u3001')
            for item2 in split_line_dunhao:
                fraction2 = reversed(word_seg(item2))
                for word in fraction2:
                    seg_line += word.decode('utf-8')+' ' 
                if item2 != split_line_dunhao[-1]:#print dunhao after fraction
                    seg_line += u'\u3001'+' '
            if item != split_line_comma[-1]:#print comma after fraction
                seg_line += u'\uff0c'+' ' 
        seg_line=re.sub(ur'([\uFF10-\uFF19]+)\s+(?=[\uFF10-\uFF19])',r'\1',seg_line)  # delete the whitespace between numbers
        seg_line=re.sub(ur'([^\xb7]*)(\s?)([\xb7])(\s?)([^\xb7]*)',r'\1\3\5',seg_line) # delete the whitespace around symbol
        seg_line=seg_line.strip()
        print seg_line    
sys.stdout = old

#++++++++++++++++++++++++++++++++++++++ Recycle Code ++++++++++++++++++++++++++++++++++++++++++++
#==================== Begin: Generate character bigram using count1w.txt ========================
# class PCdist(dict):
#     "A probability distribution estimated from counts in datafile based on Chinese characters."
#     def __init__(self, data=[],  missingfn=None):
#         for key,count in data:
#             key = key.decode('utf-8')
#             for i in range(len(key)):
#                 self[key[i]] = self.get(key[i], 0) + int(count)

#         self.N = float(sum(self.itervalues()))
#         # for key in self:
#         #     print key, self[key]
#         # print self.N
#         self.missingfn = missingfn or (lambda k, N: 1./float(N) )
    
#     def __call__(self, key): 
#         if key in self: 
#             return self[key]/self.N  
#         else: 
#             return self.missingfn(key, self.N)#I change it to 1/2N here, not really necessary.

# class PC2dist(dict):
#     "A probability distribution estimated from counts in datafile based on Chinese characters."
#     def __init__(self, data=[],  missingfn=None):
#         for key,count in data:
#             key = key.decode('utf-8')
#             self["<S>"+key[0]] = self.get("<S>"+key[0], 0) + int(count)
#             for i in range(len(key)-1):
#                 self[key[i:i+2]] = self.get(key[i:i+2], 0) + int(count)
#             self[key[-1]+"</S>"] = self.get(key[-1]+"</S>", 0) + int(count)

#         self.N = float(sum(self.itervalues()))
#         # for key in self:
#         #     print key, self[key]
#         # print self.N
#         global delta
#         self.missingfn = missingfn or (lambda k, N: delta/( float(N)*delta+ PCw(k[0]) ) )
    
#     def __call__(self, key): 
#         if key in self: 
#             return self[key]/self.N  
#         else: 
#             return self.missingfn(key, self.N)#I change it to 1/2N here, not really necessary.

# def avoid_long_words_character(word, N):
#     word = word.decode('utf-8')
#     sum_prob = 0
#     sum_prob += log_prob( PCw("<S>"+word[0]) )
#     for i in range(len(word)-1):
#         sum_prob += log_prob( PCw(word[i:i+2]))
#     sum_prob += log_prob(PCw(word[-1]+"</S>"))
#     global base 
#     return base**(sum_prob)

# PC2w = PC2dist(datafile(opts.counts1w))
# PCw = PCdist(datafile(opts.counts1w))
#==================== End: Generate character bigram using count1w.txt ========================
