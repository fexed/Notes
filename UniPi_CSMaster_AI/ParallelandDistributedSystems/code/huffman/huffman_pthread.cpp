#include "huffman.cpp"
#include "utimer.cpp"
#include <algorithm>
#include <pthread.h>

#define MAX_THREADS 10
#define PORTION_SIZE 1000

typedef struct {
    shared_ptr<string> text;
    vector<char> items;
    vector<int> frequencies;
} WorkerData;
unsigned int currentStartingPosition = 0;
pthread_mutex_t farmMutex;

void* computePortionData(void* param) {
    WorkerData* data = (WorkerData*)param;
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
    if (argc != 2) {
        cout << "Usage: " << argv[0] << " <filename>" << endl;
        return -1;
    }

    ifstream file(argv[1]);
    if (!file) {
        cout << "Cannot open: " << argv[1] << endl;
        return -2;
    }

    string fileContent;
    getline(file, fileContent);
    file.close();
    shared_ptr<string> text = make_shared<string>(fileContent);
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
        WorkerData data[MAX_THREADS];
        int numPortions = fileContent.length() / PORTION_SIZE;
        int start = 0;

        for (int i = 0; i < MAX_THREADS; i++) {
            data[i].text = text;

            if (pthread_create(&threads[i], NULL, computePortionData, (void*)&data[i]) != 0) {
                perror("Error creating thread");
                return 1;
            }
        }
        for (int i = 0; i < MAX_THREADS; i++) {
            if (pthread_join(threads[i], NULL) != 0) {
                perror("Error joining thread");
                return 1;
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