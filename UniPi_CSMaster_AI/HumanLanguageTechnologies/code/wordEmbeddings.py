# pip3 install gensim

import urllib.request
import os
import re
import logging
from gensim.models import Word2Vec
import numpy as np
from numpy.linalg import norm
from sklearn.metrics.pairwise import cosine_similarity


def most_similar_l2(word, wv, topn=10):
    from gensim import matutils
    vector = wv[word]
    dists = np.linalg.norm(wv.vectors - vector, axis=1)
    best = matutils.argsort(dists, topn=topn)
    return [(wv.index_to_key[sim], float(dists[sim]))
            for sim in best[1:]] # skip word itsels (dist=0)


def cosine(x, y):
    return x.dot(y)/(norm(x)*norm(y))


def download_file(url, local_file):
    """
    Helper function to download a file and store it locally
    """
    if os.path.exists(local_file):
        print('Already downloaded')
    else:
        print('Downloading')
        with urllib.request.urlopen(url) as opener, open(local_file, mode='wb') as outfile:
                    outfile.write(opener.read())


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.WARN)
print("Let's use a corpus from Peter Norvig")
big_text_file = 'data/big.txt'
download_file('http://norvig.com/big.txt', big_text_file)

with open(big_text_file, mode='r', encoding='utf-8') as infile:
    for i in range(10):
        print(infile.readline(), end='')

sentences = []
with open(big_text_file, mode='r', encoding='utf-8') as infile:
    for line in infile:
        sentences.append(re.split('[\W\d_]+', line.lower()))

model = Word2Vec(sentences, vector_size=100, window=10, min_count=5, sg=1, epochs=20, workers=8, negative=10)

print("Embedding vectors are stored in model.vw, here the vector of a word")
print(model.wv['project'])

print("The method most_similar returns the top 10 closest words to the input, according to cosine similarity of their embedding vectors")
print(model.wv.most_similar('watson'))
print(cosine(model.wv['watson'], model.wv['holmes']))
print(most_similar_l2('watson', model.wv))

print("Compute the similarity of among all embeddings and plot them")
similarities = cosine_similarity(model.wv.vectors)
print(similarities[1,2])

print("Evaluate the model with evaluate_word_analogies")
print("Load the analogy test and measure the accuracy")
test_file = 'data/questions-words.txt'
download_file('http://download.tensorflow.org/data/questions-words.txt', test_file)
print("The file contains a series of analogy pairs")
with open(test_file) as f:
    for i in range(10):
        print(f.readline(), end='')

score, sections = model.wv.evaluate_word_analogies(test_file)

for sec in sections:
    correct, incorrect = len(sec['correct']), len(sec['incorrect'])
    tot = correct + incorrect
    print(f"{sec['section']}: {correct*100./tot:.2f}% ({correct}/{tot})")
