import argparse
import json
from random import *


def parse_args():
    parser = argparse.ArgumentParser(description="TODO")
    data_parser = parser.add_mutually_exclusive_group(required=False)
    data_parser.add_argument("--type", type=str, required=False, default="NULL",
                            help="<normal> for a normal dataset or <anomalous> whit a anomalous day")
    data_parser.add_argument("--days", type=int, required=False, default=5,
                            help = "number of days")
    return parser.parse_args()


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

# Create a anomalous dataser for a day
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

#MAIN
args = parse_args()
datasetType = args.type
numdays = args.days
master_dataset = []
if (datasetType == "normal"):
    for i in range(numdays):
        master_dataset += createDataset()
    print("Dataset created")
    dataToJson(master_dataset, "dataset.json")
elif(datasetType == "anomalous"):
    for i in range(numdays-1):
        master_dataset += createDataset()
    master_dataset += createAnomalousDataset()
    print("Anomalous Dataset created")
    dataToJson(master_dataset, "anomalousDataset.json")
else:
    print("Dataset not created")
