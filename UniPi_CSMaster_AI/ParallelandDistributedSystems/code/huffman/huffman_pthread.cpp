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
} FarmWorkerData;
unsigned int currentStartingPosition = 0;
pthread_mutex_t farmMutex;

void* computePortionData(void* param) {
    FarmWorkerData* data = (FarmWorkerData*)param;
    int startingPosition;

    while(1) {
        pthread_mutex_lock(&farmMutex);
        startingPosition = currentStartingPosition++;
        pthread_mutex_unlock(&farmMutex);

        if (startingPosition*PORTION_SIZE >= data->text->length()) break;
        string localPortion = data->text->substr(startingPosition*PORTION_SIZE, PORTION_SIZE);
        readFileData(localPortion, data->items, data->frequencies);
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
    int size = 0;
    string encoded;

    {
        utimer tthreads("Huffman codes pthread");
        pthread_t threads[MAX_THREADS];
        FarmWorkerData data[MAX_THREADS];
        int numPortions = text->length() / PORTION_SIZE;
        int start = 0;

        for (int i = 0; i < MAX_THREADS; i++) {
            data[i].text = text;

            if (pthread_create(&threads[i], NULL, computePortionData, (void*)&data[i]) != 0) {
                cout << "Error creating thread" << endl;
                return -3;
            }
        }

        for (int i = 0; i < MAX_THREADS; i++) {
            if (pthread_join(threads[i], NULL) != 0) {
                cout << "Error joining thread" << endl;
                return -4;
            } else {
                for (int j = 0; j < data[i].items.size(); j++) {
                    std::vector<char>::iterator itr = std::find(items.begin(), items.end(), data[i].items[j]);
                    if (itr != items.cend()) {
                        frequencies[std::distance(items.begin(), itr)] += data[i].frequencies[j];
                    } else {
                        items.push_back(data[i].items[j]);
                        frequencies.push_back(data[i].frequencies[j]);
                    }
                }
            }
        }

//        readFileData(text, items, frequencies);

//        size = items.size();
//        auto root = buildHuffmanTree(items, frequencies, size);

//        generateCodes(root, list, top, codes);
//        encoded = encodeFile(text, codes);
    }
    
    return 0;
}