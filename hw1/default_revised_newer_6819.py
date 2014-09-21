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
def make_entry(word = '', start_pos = 0, log_prob = -1e309, back_pointer = None):#notice the -INF log_prob 
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
        
        self.missingfn = (lambda k, N: 1./N)
    
    def __call__(self, key): 
        if key in self: 
            return self[key]/self.N  
        else: 
            return self.missingfn(key, self.N)#I change it to 1/2N here, not really necessary.
                
Pw  = Pdist(datafile(opts.counts1w))#load in the probability table.

def word_seg(input_line):
    line_len = len(input_line)    
    word_max_len = 5
    chart = []   
    myheap =  []
    for i in range(line_len):
        chart.append(make_entry())
    #initialize heap
    for i in range(word_max_len):
        current_word = input_line[0:i+1].encode('utf-8')
        found_logprob = log10(Pw.__call__(current_word))#log_prob
        not_found = log10(Pw.missingfn(current_word,Pw.N))#log_prob, notice minus value
        if found_logprob > not_found:
            current_entry = make_entry(current_word, 0, found_logprob, None)
            heappush(myheap, current_entry)#myheap.append(current_entry)
            
    #if no matching word at position 0, insert the one or two characters to initialize heap
    if len(myheap) ==0 : 
        heappush(myheap, make_entry(input_line[0:2].encode('utf-8'),0, not_found, None)) #the log_prob = not_found here, you can change it.
    #####################################complete initialization######################
        
    #####################################start while loop############################## 
    #starting the while loop 
    end_index = 0
    #print 'heap initialized:' #these lines help to monitor the process, you can uncomment them
    #dump_heap(myheap)
    #print '*'*100
    while myheap:        
        myheap = sorted(myheap, key = lambda entry:entry[1])#sort by start_position
        top_entry  = myheap.pop()
        #print 'top entry:   '
        dump_entry(top_entry)
        #print 'currrent heap:   '
        #dump_heap(myheap)

	
        #be careful with unicode word length    
        current_word_length = len(top_entry[0].decode('utf-8'))
        end_index = (top_entry[1]) + current_word_length - 1                            
        #print end_index, current_word_length
        if chart[end_index][2] < top_entry[2]: #if popup word is better, replace the old one
            chart[end_index] = top_entry
        insert_flag = 0 #monitor the insert action below, 
        #print "current chart:   "	
        #dump_heap(chart) 
        ##############################################################################################
        #INSERT NEW WORD "KEY PROCESS"  
        #this process should be changed according to our discussion today
        for i in range(word_max_len):
            #i = word_max_len - t#backward lookup
            if end_index+i <= line_len-1:
                current_word  =input_line[end_index + 1: end_index + 1 + i].encode('utf-8')
                
                found_logprob = log10(Pw.__call__(current_word))
                not_found  = log10(Pw.missingfn(current_word,Pw.N))
                if found_logprob> not_found:
                    insert_flag = 1
                    current_entry = make_entry(current_word, end_index+1, top_entry[2] + found_logprob, end_index)
                    #print i
                    myheap.append(current_entry)
                #elif insert_flag ==1:
                #    current_entry = make_entry(current_word, end_index+1, top_entry[2] + not_found , end_index)
                #    myheap.append(current_entry)
                    
        #print insert_flag
        if end_index != line_len-1:#if no matching word, push next two words into heap
            if insert_flag == 0:
                current_word = input_line[end_index + 1: end_index + 3].encode('utf-8')
                current_entry = make_entry(current_word,end_index+1,top_entry[2]+log10(Pw.missingfn(current_word,Pw.N)),end_index)
                myheap.append(current_entry)
                #current_word = input_line[end_index + 1: end_index + 3].encode('utf-8')
                #current_entry = make_entry(current_word,end_index+1,top_entry[2]+log10(Pw.missingfn(current_word,Pw.N)),end_index)
                #myheap.append(current_entry)
                #print 'GUESS TWO CHARACTERS!!!!!!!!!!!!! '
                #print
                
                #print end_index, top_entry[0].decode('utf-8'), top_entry[1],current_word_length, current_entry[0].decode('utf-8')
                #print 'heap after insert newword:    '
                #dump_heap(myheap)
    #print '*'*100
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
