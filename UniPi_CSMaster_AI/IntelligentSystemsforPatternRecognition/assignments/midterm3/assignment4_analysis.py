# using https://github.com/spro/char-rnn.pytorch
import sys
import csv
import random
import string
import math
import torch
import torch.nn as nn
import numpy as np
from torch.autograd import Variable
from difflib import SequenceMatcher


# Turning a string into a tensor
def char_tensor(string):
    tensor = torch.zeros(len(string)).long()
    for c in range(len(string)):
        try:
            tensor[c] = all_characters.index(string[c])
        except:
            continue
    return tensor


def generate(decoder, prime_str='A', predict_len=100, temperature=0.8, proper_ending=True):
    hidden = decoder.init_hidden(1)
    prime_input = Variable(char_tensor(prime_str).unsqueeze(0))
    predicted = prime_str

    # Use priming string to "build up" hidden state
    for p in range(len(prime_str) - 1):
        _, hidden = decoder(prime_input[:,p], hidden)

    inp = prime_input[:,-1]

    for p in range(predict_len):
        output, hidden = decoder(inp, hidden)

        # Sample from the network as a multinomial distribution
        output_dist = output.data.view(-1).div(temperature).exp()
        # ugly fix for "probability tensor contains either `inf`, `nan` or element < 0"
        output_dist[output_dist == float("Inf")] = 1.0e+10
        top_i = torch.multinomial(output_dist, 1)[0]

        # Add predicted character to string and use as next input
        predicted_char = all_characters[top_i]
        predicted += predicted_char
        inp = Variable(char_tensor(predicted_char).unsqueeze(0))

    if (proper_ending):
        while (predicted[-1] != "."):  # generates until the next "."
            output, hidden = decoder(inp, hidden)

            output_dist = output.data.view(-1).div(temperature).exp()
            output_dist[output_dist == float("Inf")] = 1.0e+10
            top_i = torch.multinomial(output_dist, 1)[0]

            predicted_char = all_characters[top_i]
            predicted += predicted_char
            inp = Variable(char_tensor(predicted_char).unsqueeze(0))

    return predicted[len(prime_str):]


#custom_sentence = "Make America Great Again"
custom_sentence = "People keep telling me orange but I still prefer pink."
temperature = 0.8

all_characters = string.printable
csv.field_size_limit(sys.maxsize)
with open("corpus.csv") as file:
    reader = csv.reader(file, delimiter=",", quotechar="\"")
    for row in reader:
        if (row[0] == "Bill Clinton"): clinton = row
        if (row[0] == "Donald Trump"): trump = row

clinton_sentences = clinton[2].replace(".", "\n").replace("!", "\n").replace("?", "\n").split("\n")
trump_sentences = trump[2].replace(".", "\n").replace("!", "\n").replace("?", "\n").split("\n")

print(clinton[0])
clinton_sentences_lengths = [len(str) for str in clinton_sentences]
clinton_sentences_avglen = float(sum(clinton_sentences_lengths))/len(clinton_sentences_lengths)
print ("The real President Clinton has an average sentence length of " + "{:5.5}".format(clinton_sentences_avglen) + " characters")
clinton_sentences_avglen = int(clinton_sentences_avglen)

clinton_RNP = torch.load("RNP_clinton.pt")

# Analysis
scores = []
for i in range(100):
    rnd_sentence = random.choice(clinton_sentences).strip()
    gen_sentence = rnd_sentence[0:5] + generate(clinton_RNP, rnd_sentence[0:5], len(rnd_sentence) - 5, temperature = temperature, proper_ending = False)
    scores.append(SequenceMatcher(None, rnd_sentence, gen_sentence).ratio())
print("The Recurrent Neural President Clinton resembles the real President Clinton at", "{:.3}%".format(np.mean(scores)*100))
scores = []
for i in range(100):
    rnd_sentence = random.choice(trump_sentences).strip()
    gen_sentence = rnd_sentence[0:5] + generate(clinton_RNP, rnd_sentence[0:5], len(rnd_sentence) - 5, temperature = temperature, proper_ending = False)
    scores.append(SequenceMatcher(None, rnd_sentence, gen_sentence).ratio())
print("The Recurrent Neural President Clinton resembles the real President Trump at", "{:.3}%".format(np.mean(scores)*100))

print("\nSample speech")
print("\"Dear Americans," + generate(clinton_RNP, "Dear Americans,", clinton_sentences_avglen*15, temperature=temperature) + '\"\n')

rnd_sentence = random.choice(clinton_sentences).strip()
print("Clinton as Clinton:\t\"[" + rnd_sentence + "]", end = "")
print(generate(clinton_RNP, rnd_sentence, clinton_sentences_avglen*5, temperature=temperature) + '\"\n')
rnd_sentence = random.choice(trump_sentences).strip()
print("Clinton as Trump:\t\"[" + rnd_sentence + "]", end = "")
print(generate(clinton_RNP, rnd_sentence, clinton_sentences_avglen*5, temperature=temperature) + '\"\n')
print("Clinton:\t\t\"[" + custom_sentence + "]", end = "")
print(generate(clinton_RNP, custom_sentence, clinton_sentences_avglen*5, temperature=temperature) + '\"\n')

print(trump[0])

trump_sentences_lengths = [len(str) for str in trump_sentences]
trump_sentences_avglen = float(sum(trump_sentences_lengths))/len(trump_sentences_lengths)
print ("The real President Trump has an average sentence length of " + "{:5.5}".format(trump_sentences_avglen) + " characters")
trump_sentences_avglen = int(trump_sentences_avglen)
trump_RNP = torch.load("RNP_trump.pt")

# Analysis
scores = []
for i in range(100):
    rnd_sentence = random.choice(trump_sentences).strip()
    gen_sentence = rnd_sentence[0:5] + generate(trump_RNP, rnd_sentence[0:5], len(rnd_sentence) - 5, temperature = temperature, proper_ending = False)
    scores.append(SequenceMatcher(None, rnd_sentence, gen_sentence).ratio())
print("The Recurrent Neural President Trump resembles the real President Trump at", "{:.3}%".format(np.mean(scores)*100))
scores = []
for i in range(100):
    rnd_sentence = random.choice(clinton_sentences).strip()
    gen_sentence = rnd_sentence[0:5] + generate(trump_RNP, rnd_sentence[0:5], len(rnd_sentence) - 5, temperature = temperature, proper_ending = False)
    scores.append(SequenceMatcher(None, rnd_sentence, gen_sentence).ratio())
print("The Recurrent Neural President Trump resembles the real President Clinton at", "{:.3}%".format(np.mean(scores)*100))

print("\nSample speech")
print("\"Dear Americans," + generate(trump_RNP, "Dear Americans,", trump_sentences_avglen*15, temperature=temperature) + '\"\n')

rnd_sentence = random.choice(trump_sentences).strip()
print("Trump as Trump:\t\t\"[" + rnd_sentence + "]", end = "")
print(generate(trump_RNP, rnd_sentence, trump_sentences_avglen*5, temperature=temperature) + '\"\n')
rnd_sentence = random.choice(clinton_sentences).strip()
print("Trump as Clinton:\t\"[" + rnd_sentence + "]", end = "")
print(generate(trump_RNP, rnd_sentence, trump_sentences_avglen*5, temperature=temperature) + '\"\n')
print("Trump:\t\t\t\"[" + custom_sentence + "]", end = "")
print(generate(trump_RNP, custom_sentence, trump_sentences_avglen*5, temperature=temperature) + '\"\n')
