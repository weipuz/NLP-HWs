
import sys, codecs, optparse, os
import math
from heapq import *


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
        
        self.missingfn = (lambda k, N: math.log( 1./self.N ) )
    def __call__(self, key): 
        if key in self: 
            
            return math.log( self[key]/self.N )
        else: 
            
            return self.missingfn(key, self.N)
                
Pw  = Pdist(datafile(opts.counts1w))#load in the probability table.
P2w = Pdist(datafile(opts.counts2w))

def cPw(word, prev):
 "The conditional probability P(word | previous-word)."
 try:
    return P2w[prev + ' ' + word]/float(Pw[prev])
 except KeyError:
    return Pw(word)

# for i in Pw.viewkeys():
#     print i
#print Pw.viewvalues()
#implement the word segmentation method
#notice encoding problem, unicode instead of bytes string
def word_seg(input_line):
    word_max_len = 10
    chart = [] #initialize chart list    
    line_len = len(input_line)
    for i in range(line_len):#notice starting point 0 or 1?
        chart.append(make_entry())
    myheap =  []#initialize heap
    for i in range(word_max_len):
        current_word = input_line[0:i+1].encode('utf-8')
        found_logprob = Pw.__call__(current_word)
        not_found = Pw.missingfn(current_word,Pw.N)

        # print current_word.decode('utf-8')
        # print found_logprob
        # print not_found

        if found_logprob > not_found:#if not missing in the database, insert into heap
            #if found ,we generate and insert the entry into the heap
            current_entry = make_entry(current_word, 0, found_logprob, None)
            heappush(myheap, current_entry)#myheap.append(current_entry)
            print "entry(" + current_word + ", 0, %f, None)"  % found_logprob
            # for item in myheap:#show items in myheap
            #     print item[0].decode('utf-8')
    #if no matching word at position 0, insert the first/two characters to initialize heap
    # print len(myheap)
    # print "************"
    if len(myheap) ==0 :
        #heappush(myheap, make_entry(input_line[0:1].encode('utf-8'),0, not_found, None))
        heappush(myheap, make_entry(input_line[0:2].encode('utf-8'), 0, not_found, None))
    #####################################complete initialization######################
    #starting the while loop 
    end_index = 0
    while myheap and end_index < line_len -1:        
        myheap = sorted(myheap, key = lambda entry: entry[2])
        top_entry  = myheap.pop()
        #be careful with unicode word length    
        #################how to count chinese words###########3#3??????????
        current_word_length = len(top_entry[0].decode('utf-8'))
	#print len(top_entry[0].decode('utf-8')),top_entry[0].decode('utf-8')
        #if current_word_length ==0: 
        #    current_word_length = 1
        
        end_index = (top_entry[1]) + current_word_length - 1
        #compare the chart table with top_entry        
        #print chart[end_index]
        
            
        
        if chart[end_index][2] < top_entry[2]:
            chart[end_index] = top_entry
        insert_flag = 0 #monitor the insert action below
        #insert each newword starting at postion end_index+1 into heap
        for i in range(word_max_len):
            current_word  =input_line[end_index + 1: end_index + 1 + i].encode('utf-8')
            found_logprob = Pw.__call__(current_word)
            not_found  = Pw.missingfn(current_word,Pw.N)
            if found_logprob > not_found: #if not missing in the database, insert into heap
                insert_flag = 1
                current_entry = make_entry(current_word, end_index+1, top_entry[2] + found_logprob, top_entry)
                myheap.append(current_entry)
        #if no matching word , insert the next one/two characters to go on until the end of sentence
        #print insert_flag
        if end_index != line_len-1:
            if insert_flag == 0:
                myheap.append(make_entry(input_line[end_index + 1: end_index + 3].encode('utf-8'),end_index+1,not_found,top_entry))
        #print end_index, top_entry[0].decode('utf-8'), top_entry[1],current_word_length, current_entry[0].decode('utf-8')
           
    #build output from chart table and backponter
    output_line  = []
    entry = chart[line_len-1]#final entry first 
#    
    output_line.append(entry[0])
    #print entry[0].decode('utf-8')
    entry =  entry[3]
    #for item in output_line:
    #    print item.decode('utf-8')
    
    while entry:#append until reach chart[0] with none backpointer
        #print entry[0]
        if entry[0] != '':
            output_line.append(entry[0])
        entry = entry[3]
        
    #print output_line
#    for item in output_line:
#        print item.decode('utf-8'),
#    print 
    return output_line
#
  #     Full width coma:                u'\uff0c'
  #     Full width period:              u'\uFF61'
  #     FULLWIDTH COLON              u'\uff1a'
  #     FullWidth Right Parenthesis:    u'\uff09'
  #     FullWidth Left Parenthesis:     u'\uff08'
  #    FullWidth Quotation Mark         u'\uff02'
  #      FULLWIDTH EXCLAMATION MARK      u'\uff01'
  #     HALFWIDTH IDEOGRAPHIC COMMA      u'\uff64'

def split_text( text ):
    delimit = [ u'\uff0c', u'\uff1a', u'\uff09', u'\uff08', u'\uff02', u'\uff01', u'\uff64']
    split_line = [text]
    newset = []
    for i in range(len(delimit)):
        d = delimit[i]
        for item in split_line:
            newset = [i for i in item.split(d) ]
            split_line = newset

    return split_line

####################################################end word_seg##################

old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)
# ignoring the dictionary provided in opts.counts
with open(opts.input) as f:
    for line in f:
        utf8line = unicode(line.strip(), 'utf-8')
        #do some preprocessing to the sentence, break it into pieces by punctuations ,
        split_line = utf8line.split(u'\uff0c')#split_text( utf8line )
        for item in split_line:
            fraction = reversed(word_seg(item))
            for word in fraction:
                print word.decode('utf-8'),
            if item != split_line[-1]:
                print u'\uff0c',
        print
sys.stdout = old
