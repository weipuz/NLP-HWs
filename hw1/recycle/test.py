import math
import sys, codecs, optparse, os
import math
from heapq import *
global total

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
def make_entry(word, start_pos, log_prob, back_pointer):

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

            return [math.log( self[key]/self.N), True]
        else:

            return [self.missingfn(key, self.N), False]

Pw  = Pdist(datafile(opts.counts1w))#load in the probability table.
total = len(Pw)

def word_seg(input_line):
    word_max_len = 10
    chart = [] #initialize chart list
    line_len = len(input_line)
    for i in range(line_len):#notice starting point 0 or 1?
        chart.append(make_entry('', 0, -10, None))
    myheap = []  #initialize heap
    for i in range(min(word_max_len, line_len)):
        current_word = input_line[0:i+1].encode('utf-8')
        pair = Pw.__call__(current_word)
        if pair[1]:   # if current_word is not missing from the dictionary
            heappush(myheap, make_entry(current_word.decode('utf-8'), 0, pair[0], None))

    if len(myheap) == 0:
        heappush(myheap, make_entry(input_line[0:1], 0, math.log(1./total), None))
    #####################################complete initialization######################
    #starting the while loop
    end_index = 0
    while myheap:

        myheap = sorted(myheap, key = lambda entry: entry[1])
        top_entry  = myheap.pop()
        current_word_length = len(top_entry[0].encode('utf-8'))
	#print len(top_entry[0].decode('utf-8')),top_entry[0].decode('utf-8')
        #if current_word_length ==0:
        #    current_word_length = 1

        end_index = (top_entry[1]) + current_word_length - 1
        #compare the chart table with top_entry
        #print chart[end_index]

        if len(chart[end_index]) != 0:
            if top_entry[2] > chart[end_index][2]:
                chart[end_index] = top_entry
            if top_entry[2] <= chart[end_index][2]:
                continue
        else:
            chart[end_index] = top_entry

    # unsolved: for loop needs to consider (end_index+1)<L, (end_index+1)=L, L<(end_index+1)<input, (end_index+1)=input
        for new_word in range((end_index + 1), min(word_max_len, line_len)):
            new_pair = Pw.__call__(new_word)
            new_entry = make_entry(new_word, end_index+1, top_entry[2]+pair[0], chart[end_index])
            if new_entry not in myheap:
                myheap.append(new_entry)




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
                #print word.decode('utf-8'),
                print word,
            if item != split_line[-1]:
                print u'\uff0c',
        print
sys.stdout = old
