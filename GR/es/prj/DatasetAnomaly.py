import json
from random import *


# Create a dataset for a day
def createDataset():
    dataset = []
    for i in range(108): # 00 to 09
        dataset.append(randint(0,10))
    for i in range(48): # 09 to 13 (Work)
        elem = randint(80,90)
        dataset.append(elem)
    for i in range(12): # 13 to 14
        elem = randint(0,10)
        dataset.append(elem)
    for i in range(48): # 14 to 18 (Work)
        elem = randint(70,80)
        dataset.append(elem)
    for i in range(36): # 18 to 21
        elem = randint(0,10)
        dataset.append(elem)
    for i in range(24): # 21 to 23 (It's time for Netflix)
        elem = randint(340,350)
        dataset.append(elem)
    for i in range(12): # 23 to 24
        dataset.append(randint(0,10))
    return dataset


# Create a dataset for an anomalous day
def createAnomalousDataset():
    dataset = []
    for i in range(108): # 00 to 09
        dataset.append(randint(0,10))
    for i in range(48): # 09 to 13 (Work)
        elem = randint(340,350)
        dataset.append(elem)
    for i in range(12): # 13 to 14
        elem = randint(0,10)
        dataset.append(elem)
    for i in range(48): # 14 to 18 (Work)
        elem = randint(70,80)
        dataset.append(elem)
    for i in range(36): # 18 to 21
        elem = randint(0,10)
        dataset.append(elem)
    for i in range(24): # 21 to 23 (It's time for Netflix)
        elem = randint(340,350)
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
for i in range(3):
    master_dataset += createDataset()
master_dataset += createAnomalousDataset()
master_dataset += createDataset()

dataToJson(master_dataset, "anomalousdataset.json")
