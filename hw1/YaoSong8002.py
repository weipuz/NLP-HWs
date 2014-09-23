#the new version written on 9.15
import sys, codecs, optparse, os
from heapq import *
from math import log10, exp
import re

debug_mode =False
#debug_mode = True
optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

def datafile(name, sep='\t'):
    "Read key,value pairs from file."
    for line in file(name):
        yield line.split(sep)

def log_prob(prob):
    if prob <= 0:
        return -1e10
    else:
        return log10(prob)/log10(2)
        
def avoid_long_words(word, N):
    "Estimate the probability of an unknown word."
    return 1./(N * exp(len(word)))
    
#entry tuple
def make_entry(word = '', start_pos = 0, log_prob = -1e10, back_pointer = None):#notice the -INF log_prob 
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
                    
class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[]):
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)
            
        self.N = float(sum(self.itervalues()))
        
        self.missingfn = (lambda k, N: 1./2/N)#1./(N+1)
    
    def __call__(self, key): 
        if key in self: 
            return self[key]/self.N  
        else: 
            return None
            #return self.missingfn(key, self.N)
def cPw(word, prev):#use smoothing here later
    "The conditional probability P(word | previous-word)."
    try:
        if P2w[prev + ' ' + word] and Pw[prev]:
            return P2w[prev + ' ' + word]/float(Pw[prev])
    except KeyError:
        if Pw(word) != None:        
            return Pw(word)
        else:
            return None
            
def assign_p(found_prob, word):
    return found_prob / float(exp(len(word.decode('utf-8'))))
        
def guess_p(word):#design guess probability
    #return len(word.decode('utf-8'))*log_prob(1./float(Pw.N+1))
    return log_prob(1./(Pw.N * exp(len(word))))
                
Pw  = Pdist(datafile(opts.counts1w))#load in the 1gram probability table.
P2w  = Pdist(datafile(opts.counts2w))#load in the 2gram probability table.
#for key ,value in P2w.iteritems():
#    print key, value

def word_seg(input_line):
    line_len = len(input_line)    
    word_max_len = 10
    chart = []   
    myheap =  []
    for i in range(line_len):
        chart.append(make_entry())
    #initialize heap
    for i in range(word_max_len):
        #i = word_max_len - t -1
        current_word = input_line[0:i+1].encode('utf-8')
        #print current_word.decode('utf-8')
        prob = cPw(current_word, "<S>")
        if prob != None:
            found_logprob = log_prob(prob)
        else:
            #print 'None'
            found_logprob = None
        #not_found = log_prob(Pw.missingfn(current_word, Pw.N))#how to know not_found

        if debug_mode:
            print found_logprob
        
        if found_logprob != None:
            assign_prob =  assign_p(found_logprob, current_word)
            current_entry = make_entry(current_word, 0, assign_prob, None)
            heappush(myheap, current_entry)#myheap.append(current_entry)
            #break
    #if no matching word at position 0, insert the one or two characters to initialize heap
    if len(myheap) ==0 : 
        for i in range(5):
            if i < line_len-1:
                word = input_line[0:i+1].encode('utf-8')
                #guess_prob  = log_prob(1./float((Pw.N+1) * 10**len(word.decode('utf-8'))))
                guess_prob  = guess_p(word)
                #print len(word.decode('utf-8'))
                heappush(myheap, make_entry(word,0, guess_prob, None))#10./(N * 10**len(word))
        
    #####################################complete initialization######################
        
    #####################################start while loop############################## 
    #starting the while loop 
    end_index = 0
    if debug_mode:
        print 'heap initialized:' #these lines help to monitor the process, you can uncomment them
        dump_heap(myheap)
        print '*'*100
    while myheap:        
        myheap = sorted(myheap, key = lambda entry:entry[1])#sort by start_position
        top_entry  = myheap.pop(0)
        if debug_mode:
            print 'top entry:   '
            dump_entry(top_entry)
            print 'currrent heap:   '
            dump_heap(myheap)

	
        #be careful with unicode word length    cPw(current_word, "<S>")
        current_word_length = len(top_entry[0].decode('utf-8'))
        end_index = (top_entry[1]) + current_word_length - 1                            
        #print end_index, current_word_length
        if chart[end_index][2] < top_entry[2]: #if popup word is better, replace the old one
            chart[end_index] = top_entry
        insert_flag = 0 #monitor the insert action below, 
        if debug_mode:
            print "current chart:   "	
            dump_heap(chart) 
        ##############################################################################################
        
        for t in range(word_max_len):
            i = word_max_len - t #backward lookup
            if end_index+i <= line_len-1:
                current_word  = input_line[end_index + 1: end_index + 1 + i].encode('utf-8')
                #print current_word.decode('utf-8')
                prev_word = chart[end_index][0]
                if cPw(current_word, prev_word) != None:
                    found_logprob = log_prob(cPw(current_word, prev_word))
                else:
                    found_logprob = None
                
                if found_logprob != None:
                    assign_prob =  assign_p(found_logprob, current_word)
                    insert_flag = 1
                    #print len(current_word.decode('utf-8'))
                    current_entry = make_entry(current_word, end_index+1, top_entry[2] + assign_prob, end_index)
                    #print i
                    if current_entry[0] not in [item[0] for item in myheap]:#prevent later arrivals
                        myheap.append(current_entry)                        
                        if debug_mode:
                            print 'insert new entry:'
                            dump_entry(current_entry)
                            
                        
                    #break
                #elif insert_flag ==1:
                #    current_entry = make_entry(current_word, end_index+1, top_entry[2] + not_found , end_index)
                #    myheap.append(current_entry)
                    
        #print insert_flag
        if end_index != line_len-1:#guess word
            if insert_flag == 0:
                
                current_word = input_line[end_index + 1: end_index + 2+1].encode('utf-8')
                #guess_prob  = log_prob(1./float((Pw.N+1) * 10**len(current_word.decode('utf-8'))))
                guess_prob  = guess_p(current_word)
                current_entry = make_entry(current_word,end_index+1,top_entry[2]+ guess_prob, end_index)
                if current_entry[0] not in [item[0] for item in myheap]:
                    myheap.append(current_entry)
                    
                if debug_mode:
                    print 'GUESS two CHARACTERS!!!!!!!!!!!!! '
                    dump_entry(current_entry)
                    
                current_word = input_line[end_index + 1: end_index + 1 +1].encode('utf-8')
                #guess_prob  = log_prob(1./float((Pw.N+1) * 10**len(current_word.decode('utf-8'))))
                guess_prob  = guess_p(current_word)
                current_entry = make_entry(current_word,end_index+1,top_entry[2]+guess_prob,end_index)
                myheap.append(current_entry)
                if current_entry not in myheap:
                    myheap.append(current_entry)
                
                if debug_mode:
                    print 'GUESS one CHARACTERS!!!!!!!!!!!!! '
                    dump_entry(current_entry)
                
                #print end_index, top_entry[0].decode('utf-8'), top_entry[1],current_word_length, current_entry[0].decode('utf-8')
        if debug_mode:
            print 'heap after insert newword:    '
            dump_heap(myheap)
            print '*'*100
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
        
        # delimit_list = [i for i in p.split(utf8line) if i != " " and i != ""]
        #     for i in delimit_list:
        # print i  
        #do some preprocessing to the sentence, break it into pieces by punctuations ,     
        split_line_comma = utf8line.split(u'\uff0c') #split by comma
        # print re.match(ur"[\u4e00-\u9fa5]", utf8line)
        seg_line=''
        for item in split_line_comma:  
            fraction2 = reversed(word_seg(item))
            for word in fraction2:
                seg_line += word.decode('utf-8') +' '
            if item != split_line_comma[-1]:#print comma after fraction
                seg_line += u'\uff0c'+' ' 
        seg_line=re.sub(ur'([\uFF10-\uFF19]+)\s+(?=[\uFF10-\uFF19])',r'\1',seg_line)  # delete the whitespace between numbers
        seg_line=seg_line.strip()
        print seg_line    
#    for line in f:        
#        utf8line = unicode(line.strip(), 'utf-8')
#        #do some preprocessing to the sentence, break it into pieces by punctuations ,      
#        split_line_comma = utf8line.split(u'\uff0c') #split by comma
#        #print     count_line_number
#        split_line_comma = utf8line.split(u'\uff0c') #split by comma
#        for item in split_line_comma:             
#            fraction2 = reversed(word_seg(item))
#            for word in fraction2:
#                print word.decode('utf-8'),  
#            if item != split_line_comma[-1]:#print comma after fraction
#                print u'\uff0c',    
#        print
            #fraction = reversed(word_seg(item))
            #for word in fraction:
            #    print word.decode('utf-8'),
            #if item != split_line[-1]:
            #    print u'\uff0c',
        
	#count_line_number = count_line_number +1
sys.stdout = old