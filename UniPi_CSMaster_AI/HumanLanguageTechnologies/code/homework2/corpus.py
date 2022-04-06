import time
from collections import namedtuple

Token = namedtuple('Token', ['id', 'form', 'pos', 'head', 'deprel'], defaults=(0,)*5)

def read_conll(in_file, max_sent=-1):
    """
    Read a CoNLL-U file from @param infile.
    @return a list of sentences. Each sentence is a list of tokens (i, form, pos, head, deprel)
    """
    sentences = []
    with open(in_file) as f:
        tokens = []
        for line in f:
            line = line.strip()
            if not line:
                sentences.append(tokens)
                tokens = []
                if len(sentences) == max_sent:
                    break
            elif line[0] != '#': # skip comments
                sp = line.split('\t')
                if '-' not in sp[0]: # multiword token
                    tokens.append(Token(int(sp[0]), sp[1], sp[4], int(sp[6]), sp[7]))
        # leftover
        if tokens:
            sentences.append(tokens)
    return sentences


def load_dataset(train_file, dev_file, test_file, max_sent=-1):
    """
    :param max_sent (int):  
    """
    print("Loading data...", end='')
    start = time.time()
    train_set = read_conll(train_file, max_sent)
    dev_set = read_conll(dev_file, max_sent/2)
    test_set = read_conll(test_file, max_sent/2)
    print(" took {:.2f} seconds".format(time.time() - start))

    print("Building parser...", end='')
    start = time.time()
    parser = Parser(train_set)
    print(" took {:.2f} seconds".format(time.time() - start))

    print("Vectorizing data...", end='')
    start = time.time()
    train_set = parser.vectorize(train_set)
    dev_set = parser.vectorize(dev_set)
    test_set = parser.vectorize(test_set)
    print(" took {:.2f} seconds".format(time.time() - start))

    print("Preprocessing training data...",)
    start = time.time()
    train_features = parser.create_features(train_set)
    dev_features = parser.create_features(dev_set)
    test_features = parser.create_features(test_set)
    print("took {:.2f} seconds".format(time.time() - start))

    return parser, train_features, dev_features, test_features
