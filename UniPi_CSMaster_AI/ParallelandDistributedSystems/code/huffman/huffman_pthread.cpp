#include "huffman.cpp"
#include "utimer.cpp"
#include <algorithm>
#include <pthread.h>

#ifndef MAX_THREADS
    #define MAX_THREADS 10
#endif
#define PORTION_SIZE 1000

typedef struct {
    shared_ptr<string> text;
    vector<char> items;
    vector<int> frequencies;
} PortionWorkerData;
unsigned int currentStartingPosition = 0;
pthread_mutex_t portionMutex;

void* computePortionData(void* param) {
    PortionWorkerData* data = (PortionWorkerData*)param;
    int startingPosition;

    while(1) {
        pthread_mutex_lock(&portionMutex);
        startingPosition = currentStartingPosition++;
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
    int index;

    while(1) {
        pthread_mutex_lock(&heapMutex);
        index = currentIndex++;
        pthread_mutex_unlock(&heapMutex);

        if(index >= data->items->size()) break;
        data->minHeap->list[index] = createNode(data->items->at(index), data->frequencies->at(index));
    }

    pthread_exit(NULL);
}

int main(int argc, char **argv) {
    ARG_CHECK

    shared_ptr<string> text = make_shared<string>(readFile(argv[1]));
    if (*text == "") return -2;

    vector<char> items;
    vector<int> frequencies;
    map<char, string> codes;
    int list[MAX_HEIGHT];
    int top = 0;
    string encoded;

    {
        utimer tthreads("Huffman codes pthread");
        pthread_t threads[MAX_THREADS];
        PortionWorkerData portionData[MAX_THREADS];

        for (int i = 0; i < MAX_THREADS; i++) {
            portionData[i].text = text;

            if (pthread_create(&threads[i], NULL, computePortionData, (void*)&portionData[i]) != 0) {
                cout << "Error creating thread" << endl;
                return -3;
            }
        }

        for (int i = 0; i < MAX_THREADS; i++) {
            if (pthread_join(threads[i], NULL) != 0) {
                cout << "Error joining thread" << endl;
                return -4;
            } else {
                for (int j = 0; j < portionData[i].items.size(); j++) {
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

        auto minHeap = createMinimumHeap(items.size());
        for (int i = 0; i < items.size(); i++) {
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
        encoded = encodeFile(*text, codes);
        
//        readFileData(text, items, frequencies);

//        size = items.size();
//        auto root = buildHuffmanTree(items, frequencies, size);

//        generateCodes(root, list, top, codes);
//        encoded = encodeFile(text, codes);
    }
    
    return 0;
}