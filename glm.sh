#!bin/sh
#train suffix tagger
python q5_perceptron.py > suffix_tagger.model

#test
python q5_test.py > q5.result

#evaluate
echo question 5 result:
python eval_tagger.py tag_dev.key q5.result