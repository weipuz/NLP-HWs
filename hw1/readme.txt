============================ Developer’s Note =========================
	In this homework, Yao Song and Rao Fu provide us with prototype code implementing the given pseduo-code. Yongyi Wu applies a different dynamic programming method using only DP charts instead of heap.

============================ Algorithm Introduction ==================
	We use a 1-d vector: charts[] to maintain the entries. The main idea is that charts[n] represent the best segment among the first n characters, so instead of generate candidates and put them in the heap, we just look for previous positions and then choose the best segmentation. Besides we predefined a ‘max_word_len’, therefore we need to look for at most ‘max_word_len’ positions in charts[] before current position.

	eg. For charts[n], we will look up from charts[n-1] … charts[n - max_word_len(if outbound then 0)], and then calculate the bigram of current entry in charts[n] and entries in {chart[n-1]…charts[n - max_word_len]}, chooses the best one and continue.

============================ File Structure ==========================
Our Code
___
	chart_based.py : It is the main file written by Yongyi Wu
	default_reviesed_newer_6819.py : It is prototype file provided by Yao Song
	proto_raof.py : It is prototype file provided by Rao Fu	
	

Run
___

python chart_based.py

OR 

python chart_based.py > output


============================ Instructor’s Note =========================


Run
---

python baseline.py | python score-segments.py

OR

python baseline.py > output
python score-segments.py -t output
rm output

Data
----

In the data directory, you are provided with counts collected from
training data which contained reference segmentations of Chinese
sentenes.

The format of the count_1w.txt and count_2w.txt is a tab separated key followed by a count:

__key__\t__count__

__key__ can be a single word as in count_1w or two words separated by a space as in count_2w.txt

