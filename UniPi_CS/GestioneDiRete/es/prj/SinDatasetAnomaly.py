import json
from random import *
import math


# Create a dataset for a day
def createDataset():
    dataset = []
    for i in range(288): # 00 to 00
        dataset.append(math.sin(i)*(randint(-2,2)))
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

dataToJson(master_dataset, "sinanomalousdataset.json")
