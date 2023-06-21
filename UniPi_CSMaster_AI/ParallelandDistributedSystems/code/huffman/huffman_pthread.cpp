#include "huffman.cpp"
#include "utimer.cpp"
#include <algorithm>
#include <pthread.h>

#ifndef MAX_THREADS
    #define MAX_THREADS 100
#endif
#define PORTION_SIZE 1000

typedef struct {
    shared_ptr<string> text;
    vector<char> items;
    vector<int> frequencies;
} PortionWorkerData;
unsigned int portionStartingPosition = 0;
pthread_mutex_t portionMutex;

void* computePortionData(void* param) {
    PortionWorkerData* data = (PortionWorkerData*)param;
    unsigned int startingPosition;

    while(1) { //TODO correct
        pthread_mutex_lock(&portionMutex);
        startingPosition = portionStartingPosition++;
        pthread_mutex_unlock(&portionMutex);

        if (startingPosition*PORTION_SIZE >= data->text->length()) break;
        string localPortion = data->text->substr(startingPosition*PORTION_SIZE, PORTION_SIZE);
        readFileData(localPortion, data->items, data->frequencies);
    }

    pthread_exit(NULL);
}

typedef struct {
    shared_ptr<MinHeap> minHeap;
    shared_ptr<vector<char>> items;
    shared_ptr<vector<int>> frequencies;
} HeapWorkerData;
unsigned int currentIndex = 0;
pthread_mutex_t heapMutex;

void* buildHeap(void* param) {
    HeapWorkerData* data = (HeapWorkerData*)param;
    unsigned int index;

    while(1) {
        pthread_mutex_lock(&heapMutex);
        index = currentIndex++;
        pthread_mutex_unlock(&heapMutex);

        if(index >= data->items->size()) break;
        data->minHeap->list[index] = createNode(data->items->at(index), data->frequencies->at(index));
    }

    pthread_exit(NULL);
}

typedef struct {
    string portion;
    shared_ptr<map<char, string>> codes;
    string encodedPortion;
} PortionEncoderData;

void* portionEncoder(void* param) {
    PortionEncoderData* data = (PortionEncoderData*)param;

    data->encodedPortion = encodeText(data->portion, *(data->codes));

    pthread_exit(NULL);
}

int main(int argc, char **argv) {
    // Checking the correct usage of this tool
    // usage: ./huffman <filename>
    ARG_CHECK

    // Reading and handling file
    shared_ptr<string> text = make_shared<string>(readFile(argv[1]));
    if (*text == "") return -2;

    // Initializing common variables
    vector<char> items;
    vector<int> frequencies;
    map<char, string> codes;
    int list[MAX_HEIGHT];
    int top = 0;
    string encoded;
    string decoded;
    pthread_t threads[MAX_THREADS]; // Threadpool

    {
        utimer tthreads("Huffman codes pthread");

        // Splits the text into portions of length PORTION_SIZE and builds the required data structure
        PortionWorkerData portionData[MAX_THREADS];
        for (int i = 0; i < MAX_THREADS; i++) {
            portionData[i].text = text;

            if (pthread_create(&threads[i], NULL, computePortionData, (void*)&portionData[i]) != 0) {
                cout << "Error creating thread" << endl;
                return -3;
            }
        }

        // Joins the threads and merges the data structures
        for (int i = 0; i < MAX_THREADS; i++) {
            if (pthread_join(threads[i], NULL) != 0) {
                cout << "Error joining thread" << endl;
                return -4;
            } else {
                for (unsigned int j = 0; j < portionData[i].items.size(); j++) {
                    std::vector<char>::iterator itr = std::find(items.begin(), items.end(), portionData[i].items[j]);
                    if (itr != items.cend()) {
                        frequencies[std::distance(items.begin(), itr)] += portionData[i].frequencies[j];
                    } else {
                        items.push_back(portionData[i].items[j]);
                        frequencies.push_back(portionData[i].frequencies[j]);
                    }
                }
            }
        }

        // Builds the minimum heap, initally just putting the data in its vectors
        auto minHeap = createMinimumHeap(items.size());
        for (unsigned int i = 0; i < items.size(); i++) {
            minHeap->list.push_back(nullptr);
        }
        HeapWorkerData heapData[MAX_THREADS];
        for (int i = 0; i < MAX_THREADS; i++) {
            heapData[i].minHeap = minHeap;
            heapData[i].items = make_shared<vector<char>>(items);
            heapData[i].frequencies = make_shared<vector<int>>(frequencies);

            if (pthread_create(&threads[i], NULL, buildHeap, (void*)&heapData[i]) != 0) {
                cout << "Error creating thread" << endl;
                return -3;
            }
        }

        for (int i = 0; i < MAX_THREADS; i++) {
            if (pthread_join(threads[i], NULL) != 0) {
                cout << "Error joining thread" << endl;
                return -4;
            }
        }

        // Sequential stage that generates the codes
        minHeap->size = items.size();
        buildMinimumHeap(minHeap);
        while (minHeap->size != 1) {
            auto left = extract(minHeap);
            auto right = extract(minHeap);

            auto top = createNode('$', left->frequency + right->frequency);

            top->left = left;
            top->right = right;

            insert(minHeap, top);
        }
        auto root = extract(minHeap);
        generateCodes(root, list, top, codes);

        // Splits the text in portions to be encoded by the threadpool
        int textLength = text->size();
        int portionSize = textLength / MAX_THREADS;
        int remaining = textLength % MAX_THREADS;
        auto it = text->begin();
        PortionEncoderData portionEncoderData[MAX_THREADS];
        for (int i = 0; i < MAX_THREADS; i++) {
            int currentPortionSize = portionSize + (remaining > 0 ? 1 : 0);

            portionEncoderData[i].portion = string(it, it + currentPortionSize);
            portionEncoderData[i].codes = make_shared<map<char, string>>(codes);

            if (pthread_create(&threads[i], NULL, portionEncoder, (void*)&portionEncoderData[i]) != 0) {
                cout << "Error creating thread" << endl;
                return -3;
            }

            it += currentPortionSize;
            remaining--;
        }

        encoded = "";

        for (int i = 0; i < MAX_THREADS; i++) {
            if (pthread_join(threads[i], NULL) != 0) {
                cout << "Error joining thread" << endl;
                return -4;
            } else {
                encoded += portionEncoderData[i].encodedPortion;
            }
        }
    }

    writeBinaryFile(string(argv[1]) + "_encoded.bin", encoded);
    
    return 0;
}