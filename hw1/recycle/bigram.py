#the new version written on 9.15
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

#output entry
def dump_entry(entry):
	if entry[3] ==None:
		print 'word=%-6s, start=%-6d, log_prob=%-12f, back_pointer=%-6s' %(entry[0].decode('utf-8'),entry[1],entry[2],entry[3])
	else:
		print 'word=%-6s, start=%-6d, log_prob=%-12f, back_pointer=%-6d' %(entry[0].decode('utf-8'),entry[1],entry[2],entry[3])
	print
          

testmode = True

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[]):
        self.N1 = 0
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)
            if int(count) == 1:
                self.N1 = self.N1+1
            
        self.N = float(sum(self.itervalues()))
        self.missingfn = (lambda k, N: 1./ N ) # longer word less likely...

    def __call__(self, key): 
        global testmode
        if key in self: 
            if testmode:
                print "Found Word %s : probability = %f logprob: %f" % (key.decode('utf-8'), self[key]/self.N, log10(self[key]/self.N)/log10(2) )
            return self[key]/self.N 
        else:
            if testmode:
                print "Not Word Found %s : assign %f logprob: %f" % ( key.decode('utf-8'), self.missingfn(key, self.N), log10(self.missingfn(key, self.N))/log10(2) )
            return self.missingfn(key, self.N)

def cPw(word, prev):
    # "Exactly unigram"
    # k = 0
    # return k*P2w(prev + ' ' + word)/float(Pw(prev)) + (1-k)*Pw(word)

    # "If found bigram prob use it, or else only use unigram"
    # try:
    #     return P2w[prev + ' ' + word]/float(Pw[prev])
    # except KeyError:
    #     return Pw(word)

    return P2w(prev + ' ' + word)/Pw(prev)



                
Pw  = Pdist(datafile(opts.counts1w))#load in the probability table.
P2w = Pdist(datafile(opts.counts2w))

#entry tuple
def make_entry(word = '', start_pos = 0, log_prob = -float("inf"), back_pointer = None):#notice the -INF [-float("inf")] log_prob 
    return (word,start_pos, log_prob, back_pointer) 

def word_seg(input_line):
    line_len = len(input_line)    
    word_max_len = 8
    chart = []  

    if line_len <= 2:
        output_line = []
        output_line.append(input_line[0:].encode('utf-8'))
        return output_line

    #initialize chart
    # for i in range( min(word_max_len, line_len) ):
    for i in range(line_len+1):
        chart.append(make_entry())
    chart[0] = make_entry('', 0, log10( Pw.missingfn("", Pw.N) )/log10(2), None)
    current_word = input_line[0].encode('utf-8')
    found_logprob = log10(cPw(current_word, " "))/log10(2)#log_prob
  
    current_entry = make_entry(current_word, 0, found_logprob, None)
    chart[1] = current_entry
    if testmode:
        print "="*80
        print "initializing..."
        dump_entry (chart[0])  
        dump_entry (chart[1])  
        print "="*80
            
    i = 2
    while i <= line_len:
        # print "*** Begin while ****"*6
        for j in range(word_max_len):
            if j == 0 :
                continue
            if j > i :
                break
            

            if testmode:
                print "~"*80
            current_word = input_line[i-j:i].encode('utf-8')
            previous_word = chart[i-j][0]


            bigram_foundlog = log10(cPw(current_word, previous_word))/log10(2);
       

            # current_word_logp_abs = (found_logprob - not_found)*len(current_word);
            
            bigram_logprob = bigram_foundlog;
            if testmode:
                print "lgP(%s | %s) = %f " % (current_word.decode('utf-8'), previous_word.decode('utf-8'), bigram_foundlog )
                print "%f <= %f + %f" %(chart[i][2],chart[i-j][2] , bigram_logprob)
                print chart[i][2] <= chart[i-j][2]  + bigram_logprob
            # print bigram_logprob
            # print bigram_notfound

            if chart[i][2] <= chart[i-j][2]  + bigram_logprob:
                chart[i] = make_entry(current_word, i-j, chart[i-j][2] + bigram_logprob, i-j)
                if testmode:
                    print "chart[%d]" %i        
                    dump_entry (chart[i])  
        # print "*** End while ****"*6     
        i = i+1;

    #build output from chart table and backponter
    output_line  = []
    entry = chart[line_len]
    output_line.append(entry[0])

    while entry[3] != None:#append all previous words until chart[0]
        output_line.append(chart[entry[3]][0])        
        entry  = chart[entry[3]]
        #print entry[3]
        if entry[3] == None or entry[1] == 0:
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
                        
            fraction2 = reversed(word_seg(item))
            for word in fraction2:
                print word.decode('utf-8'),
                    
            if item != split_line_comma[-1]:#print comma after fraction
                print u'\uff0c',	
        print
sys.stdout = old
