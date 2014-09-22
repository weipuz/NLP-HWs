# NLP-hw1:
# Using heap-based DP algorithm given in pseduo-code, applied bi-gram model and good turing smooth.
# https://class.coursera.org/nlp/lecture/32
# 
# command refs:
# python hw1.py -i data/line1
# python hw1.py | python score-segements.py

import sys, codecs, optparse, os
from heapq import *
from math import log10

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

# Global Variables 
test_mode = True
word_max_len = 6

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
	if prob <= 0:
		return -1e10
	else:
		return log10(prob)/log10(2)

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    self.c_0 = 0;
    def __init__(self, data=[]):
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)
            if int(count) == 1:
                self.c_0 = self.c_0 + 1

            
        self.N = float(sum(self.itervalues()))
        
        self.missingfn = (lambda k, N: self.c_0/N) # little trick. (lambda k, N: 10./N*10**len(k))
    
    def __call__(self, key): 
        if key in self: 
            return self[key]/self.N  
        else: 
            print "Hahayou!"
            print self.c_0
            return self.missingfn(key, self.N)

Pw  = Pdist(datafile(opts.counts1w))

#entry tuple
def make_entry(word = '', start_pos = 0, log_prob = -1e10, back_pointer = None):#notice the -INF log_prob 
    return (word,start_pos, log_prob, back_pointer)

def word_seg(input_line):
    global test_mode, word_max_len
       
    chart = []              # 1-d DP chart
    candidates =  []        # a prior list/heap contains possible words generated
    line_len = len(input_line) 

    #======================= Initialize Candidates Chart & Heap =======================
    #initialize log-prob of all chart entries as -INF
    for i in range(line_len):
        chart.append(make_entry())

    for i in range(word_max_len):
        word = input_line[0:i+1].encode('utf-8')
        found_logprob = log_prob( Pw(word) )
        entry = make_entry(word, 0, found_logprob, None)
        #if found_logprob > chart[i+1][2]:
        heappush(candidates, entry)      
        chart[i+1] = entry
        dump_entry( entry )
    
    heapify(candidates)
    if test_mode:
        print "="*6,"Initialize Candidates Chart & Heap ", "="*6
        print
        dump_heap(candidates)
        print "="*6," Initialization Complete ", "="*6
    #=============================== Initialization Complete ===========================
        
    #=============================== Start While Loop ==================================
    while candidates:        
        #Sort Candidates By Start Position
        candidates = sorted(candidates, key = lambda entry:entry[1])
        dump_heap(candidates)
        top_entry  = heappop(candidates)
      
        #be careful with unicode word length    
        word_length = len(top_entry[0].decode('utf-8'))
        end_index = top_entry[1] + word_length - 1                            
        #print end_index, current_word_length
        if chart[end_index][2] < top_entry[2]: #if popup word is better, replace the old one
            chart[end_index] = top_entry
      
        ##############################################################################################
        #INSERT NEW WORD "KEY PROCESS"  
        #this process should be changed according to our discussion today
        for i in range(word_max_len):
            #i = word_max_len - t#backward lookup
            if end_index+i <= line_len-1:
                word  = input_line[end_index + 1: end_index + 1 + i].encode('utf-8')
                found_logprob = log_prob( Pw(word) )
                entry = make_entry(word, end_index+1, found_logprob, end_index)
                #if found_logprob > chart[i+1][2]:
                heappush(candidates, entry)      
                chart[i+1] = entry
                dump_entry( entry )
    ################################################end while loop #######################################            
                
    #build output from chart table and backponter
    output_line  = []#initialize output line
    entry = chart[line_len-1]#final entry first 
    output_line.append(entry[0])
    if entry[3] == None:#if no previous word, returns
        return output_line
        
    while entry[3] != None:#append all previous words until chart[0]
        output_line.append(chart[entry[3]][0])        
        entry  = chart[entry[3]]
        #print entry[3]
        if entry[3] == None:
            return output_line
####################################################end word_seg##################

old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)
# ignoring the dictionary provided in opts.counts
with open(opts.input) as f:
    #count_line_number = 1
    for line in f:        
        utf8line = unicode(line.strip(), 'utf-8')
        #do some preprocessing to the sentence, break it into pieces by punctuations ,      
        split_line_comma = utf8line.split(u'\uff0c') #split by comma
        #print     count_line_number
        for item in split_line_comma:
            split_line_dunhao = item.split(u'\u3001') #split by dunhao
            for item2 in split_line_dunhao:
                
                fraction2 = reversed(word_seg(item2))
                for word in fraction2:
                    print word.decode('utf-8'),
                if item2 != split_line_dunhao[-1]:#print dunhao at after fraction2
                    print u'\u3001',
        if item != split_line_comma[-1]:#print comma after fraction
            print u'\uff0c',    
            #fraction = reversed(word_seg(item))
            #for word in fraction:
            #    print word.decode('utf-8'),
            #if item != split_line[-1]:
            #    print u'\uff0c',
        print
    #count_line_number = count_line_number +1
sys.stdout = old
