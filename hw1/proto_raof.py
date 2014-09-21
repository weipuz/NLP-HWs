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

        self.missingfn = (lambda k, N: math.log( 10./10**len(k)*self.N, 10 ) )
    def __call__(self, key):
        if key in self:

            return [math.log( self[key]/self.N, 10), True]
        else:

            return [self.missingfn(key, self.N), False]

Pw  = Pdist(datafile(opts.counts1w))#load in the probability table.
total = len(Pw)




def word_seg(input_line):
    word_max_len = 10
    #print "input_line length: ", len(input_line)
    chart = []
    #chart = []*len(input_line) #initialize chart list
    #print "chart length: ", len(chart)
    line_len = len(input_line)
    for i in range(line_len):#notice starting point 0 or 1?
        chart.append(make_entry('', 0, float("-inf"), None))
    #print "chart length: ", len(chart)
    myheap = []  #initialize heap
    #print min(word_max_len, line_len)
    min_value = min(word_max_len, line_len)
    for i in range(min_value):
        current_word = input_line[0:i+1].encode('utf-8')
        #print current_word.decode('utf-8')
        pair = Pw.__call__(current_word)
        if pair[1]:   # if current_word is not missing from the dictionary
            myheap.append(make_entry(current_word, 0, pair[0], None))
            #print "found words: ", current_word.decode('utf-8')
            #heappush(myheap, make_entry(current_word, 0, pair[0], None))
    # while myheap:
    #     my_entry =  myheap.pop()
    #     print my_entry[0].decode('utf-8'), my_entry[1], my_entry[2], my_entry[3]
    if len(myheap) == 0:
        #heappush(myheap, make_entry(input_line[0:1].encode('utf-8'), 0, math.log(10./10**len(input_line[0:1])*total, 10), None))
        myheap.append(make_entry(input_line[0:1].encode('utf-8'), 0, math.log(10./10**len(input_line[0:1])*total, 10), None))
    #####################################complete initialization######################
    #starting the while loop
    end_index = 0
    while myheap:
        #print 'round begin'
        myheap = sorted(myheap, key = lambda entry: entry[1])
        # for m in range(len(myheap)):
        #     print "word ", myheap[m][0].decode('utf-8'), "start: ", myheap[m][1], "logprob: ", myheap[m][2], "back: ", myheap[m][3]
        top_entry  = myheap.pop(0)
        #print "top_entry: ", top_entry[0].decode('utf-8')
        #print "top_entry: " + top_entry[0].decode('utf-8')
        # while myheap:
        #     temp = myheap.pop()
        #     print temp[0].decode('utf-8'), temp[1], temp[2]
        # print 'round end'
        #print top_entry[0].decode('utf-8')
        current_word_length = len(top_entry[0].decode('utf-8'))
        #print "current_word_length: ", current_word_length
        #print current_word_length
	#print len(top_entry[0].decode('utf-8')),top_entry[0].decode('utf-8')
        #if current_word_length ==0:
        #    current_word_length = 1

        end_index = (top_entry[1]) + current_word_length - 1
        #compare the chart table with top_entry
        #print chart[end_index]

        if chart[end_index][2] != float("-inf"):
            if top_entry[2] > chart[end_index][2]:
                #print top_entry[0].decode('utf-8') + ">" + chart[end_index][0].decode('utf-8')
                chart[end_index] = top_entry
                #print "top_entry > prev: ", chart[end_index][0].decode('utf-8')
            if top_entry[2] <= chart[end_index][2]:
                #print "top_entry <= prev: ", chart[end_index][0].decode('utf-8')
                #print top_entry[0].decode('utf-8') + "<=" + chart[end_index][0].decode('utf-8')
                continue
        else:
            #print chart[end_index][0].decode('utf-8') + "=" + top_entry[0].decode('utf-8')
            chart[end_index] = top_entry
            #print "chart has no prev: ", chart[end_index][0].decode('utf-8')
        flag = False
        # if (end_index+1) == min_value:
        #     print "== "
        #     print range((end_index + 1), min(word_max_len, line_len))
        # elif (end_index+1) > word_max_len:
        #     print "> "
        #     print range((end_index + 1), min(word_max_len, line_len))
        # else:
        #     print "<"
        #     print range((end_index + 1), min(word_max_len, line_len))
    # unsolved: for loop needs to consider (end_index+1)<L, (end_index+1)=L, L<(end_index+1)<input, (end_index+1)=input
        if (end_index + 1) < line_len:
            if (end_index + word_max_len + 1) < line_len:
                end = word_max_len
            else:
                end = line_len
            for j in range((end_index + 1), (end_index + end + 1)):
                #print "Notice"
                #print type(input_line[new_word])
                new_word = input_line[end_index+1:j].encode('utf-8')
                new_pair = Pw.__call__(new_word)
                #print new_pair[0]
                if new_pair[1]:
                    flag = True
                    #print new_word.decode('utf-8')
                    #heappush(myheap, make_entry(new_word, end_index+1, top_entry[2]+new_pair[0], end_index))
                    myheap.append(make_entry(new_word, end_index+1, top_entry[2]+new_pair[0], end_index))
                    #print "found words 2: ", new_word.decode('utf-8'), "start: ", end_index+1, "logprob: ", top_entry[2]+new_pair[0], "back: ", end_index - current_word_length + 1

            if not flag: # myheap is empty
                #heappush(myheap, make_entry(input_line[(end_index+1):(end_index+2)].encode('utf-8'), end_index+1, top_entry[2]+math.log(10./10**len(input_line[(end_index+1):(end_index+2)])*total, 10), end_index))
                myheap.append(make_entry(input_line[(end_index+1):(end_index+2)].encode('utf-8'), end_index+1, top_entry[2]+math.log(10./10**len(input_line[(end_index+1):(end_index+2)])*total, 10), end_index))
                #print "active insert: ", input_line[(end_index+1):(end_index+2)].encode('utf-8').decode('utf-8'), "start: ", end_index+1, "logprob: ", top_entry[2]+math.log(10./10**len(input_line[(end_index+1):(end_index+2)])*total, 10), "back: ", end_index - current_word_length + 1
    # while myheap:
    #     my_entry =  myheap.pop()
    #     print my_entry[0].decode('utf-8'), my_entry[1], my_entry[2], my_entry[3]
            # new_entry = make_entry(new_word, end_index+1, top_entry[2]+new_pair[0], end_index)
            # if new_entry not in myheap:
            #     myheap.append(new_entry)
        # reversed(myheap)
        # while myheap:
        #     temp1 = myheap.pop()
        #     print "reversed: " + temp1[0].decode('utf-8'), temp1[1], temp1[2]





    #build output from chart table and backponter
    # print "final chart"
    # for n in range(len(chart)):
    #     print chart[n][0].decode('utf-8'), chart[n][1], chart[n][2], chart[n][3]
    output_line  = [] 
    entry = chart[line_len-1]#final entry first
    output_line.append(entry[0])
    # print "the last item: ", entry[0].decode('utf-8'), entry[3]
    # #print "Final chart length: ", len(chart)
    # output_line.append(entry[0])
    # print output_line[0].decode('utf-8')
    # #entry =  entry[3]
    while entry[3] is not None:
        output_line.append(chart[(entry[3])][0])
        #print "insert word: ", chart[(entry[3])][0].decode('utf-8')
        entry = chart[(entry[3])]
        #print "back: ", entry[3]
    # if entry[3]:
    #      entry = chart[(entry[3])]
    #      while entry:#append until reach chart[0] with none backpointer
    #     #print entry[0]
    #         if entry[0] != '':
    #             output_line.append(entry[0])

    #         if entry[3]:
    #             entry = chart[(entry[3])]
    #         else:
    #             break
    # print "output_line: "
    # for n in range(len(output_line)):
    #     print output_line[n].decode('utf-8')

    

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
        for item in split_line:   # item is type unicode
            fraction = reversed(word_seg(item))
            for word in fraction:
                print word.decode('utf-8'),
            if item != split_line[-1]:
                print u'\uff0c',
        print 
sys.stdout = old
