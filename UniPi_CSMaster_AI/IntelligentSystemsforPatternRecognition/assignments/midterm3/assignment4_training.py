# using https://github.com/spro/char-rnn.pytorch
import sys
import csv
import random
import string
import math
import torch
import torch.nn as nn
from torch.autograd import Variable
from tqdm import tqdm
from model import CharRNN


# Turning a string into a tensor
def char_tensor(string):
    tensor = torch.zeros(len(string)).long()
    for c in range(len(string)):
        # encodes each character with its string.printable index
        try:
            tensor[c] = all_characters.index(string[c])
        except:
            continue
    return tensor


def save(model, filename):
    torch.save(model, filename)
    print('Saved as %s' % filename)


def random_training_set(text, chunk_len, batch_size):
    text_len = len(text)
    inp = torch.LongTensor(batch_size, chunk_len)
    target = torch.LongTensor(batch_size, chunk_len)
    for bi in range(batch_size):  # we produce batch_size batches
        # each batch has a chunk_len length portion of the corpus
        start_index = random.randint(0, text_len - chunk_len)
        end_index = start_index + chunk_len + 1
        chunk = text[start_index:end_index]
        inp[bi] = char_tensor(chunk[:-1])
        target[bi] = char_tensor(chunk[1:])
    inp = Variable(inp)
    target = Variable(target)
    return inp, target


def train(model, inp, target, chunk_len, batch_size):
    hidden = model.init_hidden(batch_size)
    model.zero_grad()
    loss = 0

    for c in range(chunk_len):
        output, hidden = model(inp[:,c], hidden)
        loss += criterion(output.view(batch_size, -1), target[:,c])

    loss.backward()
    decoder_optimizer.step()

    return loss.data / chunk_len


model = "gru"
n_epochs = 2000
hidden_size = 250
n_layers = 2
learning_rate = 0.015
chunk_len = 250
batch_size = 100

csv.field_size_limit(sys.maxsize)
with open("corpus.csv") as file:
    reader = csv.reader(file, delimiter=",", quotechar="\"")
    for row in reader:
        if (row[0] == "Bill Clinton"): clinton = row
        if (row[0] == "Donald Trump"): trump = row

# to build the sentences we split at each sentence delimiter: ".", "!", "?" and "\n"
clinton_sentences = clinton[2].replace(".", "\n").replace("!", "\n").replace("?", "\n").split("\n")
print(clinton[0], len(clinton[2]))
print(random.choice(clinton_sentences))

trump_sentences = trump[2].replace(".", "\n").replace("!", "\n").replace("?", "\n").split("\n")
print(trump[0], len(trump[2]))
print(random.choice(trump_sentences))

all_characters = string.printable  # printable characters of the current system
clinton_RNP = CharRNN(
    len(all_characters),  # input size
    hidden_size, # 250 hidden units per layer
    len(all_characters),  # output size
    model=model,  # gru
    n_layers=n_layers,  # 2 layers
)
decoder_optimizer = torch.optim.Adam(clinton_RNP.parameters(), lr=learning_rate)
criterion = nn.CrossEntropyLoss()
print("Training \"Clinton Recurrent Neural President\" for %d epochs..." % n_epochs)
for epoch in tqdm(range(1, n_epochs + 1)):
    loss = train(clinton_RNP, *random_training_set(clinton[2], chunk_len, batch_size), chunk_len, batch_size)

save(clinton_RNP, "RNP_clinton.pt")

trump_RNP = CharRNN(
    len(all_characters),  # input size
    hidden_size, # 250 hidden units per layer
    len(all_characters),  # output size
    model=model,  # gru
    n_layers=n_layers,  # 2 layers
)
decoder_optimizer = torch.optim.Adam(trump_RNP.parameters(), lr=learning_rate)
criterion = nn.CrossEntropyLoss()
print("Training \"Trump Recurrent Neural President\" for %d epochs..." % n_epochs)
for epoch in tqdm(range(1, n_epochs + 1)):
    loss = train(trump_RNP, *random_training_set(trump[2], chunk_len, batch_size), chunk_len, batch_size)

save(trump_RNP, "RNP_trump.pt")
