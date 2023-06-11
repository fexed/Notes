#include "huffman.cpp"
#include "utimer.cpp"
#include <ff/ff.hpp>
#include <ff/pipeline.hpp>

#ifndef MAX_THREADS
    #define MAX_THREADS 100
#endif
#ifndef VERIFY
    #define VERIFY true
#endif
#define PORTION_SIZE 1000

using namespace ff;

struct Partitioner: ff_node_t<string, string> {
    string text;

    Partitioner(const string& param) : text(param) {}

    string* svc(string* ignored) {
        unsigned int pos = 0;

        while(pos * PORTION_SIZE <= text.length()) {
            string* portion = new string(text.substr(pos*PORTION_SIZE, PORTION_SIZE));
            ff_send_out(portion);
            pos++;
        }
        return EOS;
    }
};

typedef struct {
    vector<char> items;
    vector<int> frequencies;
} PortionWorkerData;
struct FarmWorker: ff_node_t<string, PortionWorkerData> {
    PortionWorkerData* data;

    FarmWorker() {
       data = new PortionWorkerData();
    }

    PortionWorkerData* svc(string* portion) {
        readFileData(*portion, data->items, data->frequencies);
        delete portion;

        return GO_ON;
    }
    
    void eosnotify(ssize_t id) {
        ff_send_out(data);
    }
};

struct FarmCollector: ff_node_t<PortionWorkerData, PortionWorkerData> {
    PortionWorkerData* data;

    FarmCollector(PortionWorkerData* portionWorkerData) : data(portionWorkerData) {}

    PortionWorkerData* svc(PortionWorkerData* portionData) {
        for (unsigned int j = 0; j < portionData->items.size(); j++) {
            std::vector<char>::iterator itr = std::find(data->items.begin(), data->items.end(), portionData->items[j]);
            if (itr != data->items.cend()) {
                data->frequencies[std::distance(data->items.begin(), itr)] += portionData->frequencies[j];
            } else {
                data->items.push_back(portionData->items[j]);
                data->frequencies.push_back(portionData->frequencies[j]);
            }
        }
        delete portionData;

        return GO_ON;
    }
};

struct HeapIndexer: ff_node_t<int> {
    int max;

    HeapIndexer(int max) : max(max) {}

    int* svc(int* ignored) {
        for (int i = 0; i < max; i++) {
            ff_send_out(new int(i));
        }

        return EOS;
    }
};

struct HeapWorker: ff_node_t<int> {
    shared_ptr<MinHeap> minHeap;
    PortionWorkerData* data;

    HeapWorker(shared_ptr<MinHeap> minHeap, PortionWorkerData* portionWorkerData) : minHeap(minHeap), data(portionWorkerData) {}

    int* svc(int* index) {
        minHeap->list[*index] = createNode(data->items[*index], data->frequencies[*index]);
        delete index;
        return GO_ON;
    }
};

struct PortionEncoder: ff_node_t<string> {
    map<char, string> codes;

    PortionEncoder(map<char, string> codes) : codes(codes) {}

    string* svc(string* portion) {
        string* encoded = new string("");
        *encoded = encodeText(*portion, codes);
        delete portion;
        return encoded;
    }
};

struct Concat: ff_node_t<string> {
    string* result;

    Concat(string* result) : result(result) {
        *result = "";
    }

    string* svc(string* portion) {
        *result += *portion;
        delete portion;
        return GO_ON;
    }
};

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

    {
        utimer tfastflow("Huffman codes fastflow");
        
        unique_ptr<Partitioner> inputStage = make_unique<Partitioner>(*text);
        vector<unique_ptr<ff_node>> portionFarmWorkers;
        for (int i = 0; i < MAX_THREADS; i++) {
            portionFarmWorkers.push_back(make_unique<FarmWorker>());
        }
        ff_Farm<PortionWorkerData> portionFarm(move(portionFarmWorkers));
        PortionWorkerData* data = new PortionWorkerData();
        unique_ptr<FarmCollector> collector = make_unique<FarmCollector>(data);

        ff_Pipe<> dataPipeline(
            inputStage,
            portionFarm,
            collector
        );
        dataPipeline.run_and_wait_end();
        
        auto minHeap = createMinimumHeap(data->items.size());
        for (unsigned int i = 0; i < data->items.size(); i++) {
            minHeap->list.push_back(nullptr);
        }
        
        unique_ptr<HeapIndexer> heapIndexer = make_unique<HeapIndexer>(data->items.size());
        vector<unique_ptr<ff_node>> heapFarmWorkers;
        for (int i = 0; i < MAX_THREADS; i++) {
            heapFarmWorkers.push_back(make_unique<HeapWorker>(minHeap, data));
        }
        ff_Farm<int> heapFarm(move(heapFarmWorkers));

        ff_Pipe<> heapPipeline(
            heapIndexer,
            heapFarm
        );
        heapPipeline.run_and_wait_end();

        minHeap->size = data->items.size();
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

        unique_ptr<Partitioner> partitioner = make_unique<Partitioner>(*text);
        vector<unique_ptr<ff_node>> encoders;
        for (int i = 0; i < MAX_THREADS; i++) {
            encoders.push_back(make_unique<PortionEncoder>(codes));
        }
        ff_OFarm<PortionEncoder> encoderFarm(move(encoders));
        unique_ptr<Concat> concat = make_unique<Concat>(&encoded);
        
        ff_Pipe<> encoderPipeline(
            partitioner,
            encoderFarm,
            concat
        );
        encoderPipeline.run_and_wait_end();
    }

    if (VERIFY) {   
        {
            utimer decode("Decoding text");
            decoded = decodeText(encoded, codes);
        }

        if (check(*text, decoded)) {
            cout << "Verified!" << endl;
        } else {
            cout << "Encoding not verified..." << endl;
        }
    }
    
    return 0;
}