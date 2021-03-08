import json
from random import *


# Create a dataset for a day
def createDataset():
    dataset = []
    for i in range(108): # 00 to 09
        dataset.append(randint(0,10))
    for i in range(48): # 09 to 13 (Work)
        elem = randint(50,70)
        dataset.append(elem)
    for i in range(12): # 13 to 14
        elem = randint(0,10)
        dataset.append(elem)
    for i in range(48): # 14 to 18 (Work)
        elem = randint(50,70)
        dataset.append(elem)
    for i in range(36): # 18 to 21
        elem = randint(0,10)
        dataset.append(elem)
    for i in range(24): # 21 to 23 (It's time for Netflix)
        elem = randint(200,250)
        dataset.append(elem)
    for i in range(12): # 23 to 24
        dataset.append(randint(0,10))
    return dataset

def dataToJson(dataset, filename):
    outfile = open(filename, "w")
    json.dump(dataset, outfile, indent=4)
    outfile.close()

def dataFromJson(filename):
    infile = open(filename, "r")
    dataset = json.load(infile)
    return dataset

master_dataset = []
for i in range(5):
    master_dataset += createDataset()

dataToJson(master_dataset, "dataset.json")
