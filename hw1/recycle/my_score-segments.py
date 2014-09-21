from __future__ import division
import optparse, sys, codecs
from collections import defaultdict

optparser = optparse.OptionParser()
optparser.add_option("-t", "--testfile", dest="testfile", default="data/my_input", help="Output from your segmenter program")
optparser.add_option("-r", "--referencefile", dest="referencefile", default="data/my_reference", help="Reference segmentation")
(opts, _) = optparser.parse_args()

if opts.testfile is None:
    test = list(sys.stdin)
else:
    with open(opts.testfile) as f:
        test = list(f)
with open(opts.referencefile) as f:
    reference = list(f)

if len(test) != len(reference):
    raise ValueError("Error: output and reference do not have identical number of lines")

def precision(reference, test):
    print reference
    print test
    if len(test) == 0:
        return None
    else:
        print "precision" + str(len(reference & test))
        print len(test)
        print str(float(len(reference & test)) / len(test))
        return float(len(reference & test)) / len(test)  # numerator is len(reference)?

def recall(reference, test):
    if len(reference) == 0:
        return None
    else:
        print "recall" + str(len(reference & test))
        print str(float(len(reference & test)) / len(reference))
        return float(len(reference & test)) / len(reference)

def fmeasure(reference, test, alpha=0.5):  # reference and test are both splitted words in a line
    p = precision(reference, test)
    r = recall(reference, test)
    if p is None or r is None:
        return None
    if p == 0 or r == 0:
        return 0
    return 1.0/(alpha/p + (1-alpha)/r)

def corpus_fmeasure(reference, test):
    """
    assumes that the input lines are in UTF-8
    used to compute f-measure for Chinese word segmentation
    sys.stdout is temporarily changed to enable debugging of UTF-8
    """
    old = sys.stdout
    sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)
    score = 0

    #test_utf8 = set(unicode(test[0], 'utf-8').split())
    #reference_utf8 = set(unicode(reference[0], 'utf-8').split())
    #if len(test_utf8) == 0: test_utf8 = set(['empty'])

    for i in range(len(reference)):
        test_utf8 = set(unicode(test[i], 'utf-8').split())
        print unicode(test[i], 'utf-8')
        reference_utf8 = set(unicode(reference[i], 'utf-8').split())
        print unicode(reference[i], 'utf-8')
        if len(test_utf8) == 0: test_utf8 = set(['empty'])
        score += fmeasure(reference_utf8, test_utf8)
    #print "Score: %.2f" % ((score/len(test))*100)
    sys.stdout = old
    return ((score/len(test))*100)

print "Score: %.2f" % corpus_fmeasure(reference, test)
#corpus_fmeasure(reference, test)