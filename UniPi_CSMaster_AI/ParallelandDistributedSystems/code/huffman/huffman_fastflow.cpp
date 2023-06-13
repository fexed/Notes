#include "huffman.cpp"
#include "utimer.cpp"
#include <ff/ff.hpp>
#include <ff/pipeline.hpp>

#ifndef MAX_THREADS
    #define MAX_THREADS 10
#endif
#ifndef VERIFY
    #define VERIFY false
#endif
#define PORTION_SIZE 1000

using namespace ff;

struct Partitioner: ff_node_t<string, string> {
    string text;

    Partitioner(const string& text) : text(text) {}

    string* svc(string* ignored) {
        unsigned int pos = 0;

        while(pos * PORTION_SIZE <= text.length()) {
            ff_send_out(new string(text.substr(pos*PORTION_SIZE, PORTION_SIZE)));
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

    FarmCollector() {
        data = new PortionWorkerData();
    }

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
    
    void eosnotify(ssize_t id) {
        ff_send_out(data);
    }
};


struct CodesBuilder: ff_node_t<PortionWorkerData, map<char, string>> {
    map<char, string>* codes;

    CodesBuilder(map<char, string>* codes) : codes(codes) {}

    map<char, string>* svc(PortionWorkerData* data) {
        int list[MAX_HEIGHT];
        int top = 0;
        auto minHeap = createMinimumHeap(data->items.size());
        for (unsigned int i = 0; i < data->items.size(); i++) {
            minHeap->list.push_back(createNode(data->items[i], data->frequencies[i]));
        }
        minHeap->size = data->items.size();
        delete data;
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
        generateCodes(root, list, top, *codes);
        return codes;
    }
};

struct EncoderData {
    string portion;
    map<char, string> codes;
};
struct EncoderPartitioner: ff_node_t<map<char, string>, EncoderData> {
    string text;

    EncoderPartitioner(const string& param) : text(param) {}

    EncoderData* svc(map<char, string>* codes) {
        unsigned int pos = 0;

        while(pos * PORTION_SIZE <= text.length()) {
            EncoderData* data = new EncoderData();
            data->portion = string(text.substr(pos*PORTION_SIZE, PORTION_SIZE));;
            data->codes = map<char, string>(*codes);
            ff_send_out(data);
            pos++;
        }
        return EOS;
    }
};

struct PortionEncoder: ff_node_t<EncoderData, string> {
    string* svc(EncoderData* data) {
        string* encoded = new string("");
        *encoded = encodeText(data->portion, data->codes);
        delete data;
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
    //cout << "Running fastflow implementation with " << MAX_THREADS << " workers" << endl;
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
        unique_ptr<FarmCollector> collector = make_unique<FarmCollector>();
        unique_ptr<CodesBuilder> coder = make_unique<CodesBuilder>(&codes);
        unique_ptr<EncoderPartitioner> partitioner = make_unique<EncoderPartitioner>(*text);
        vector<unique_ptr<ff_node>> encoders;
        for (int i = 0; i < MAX_THREADS; i++) {
            encoders.push_back(make_unique<PortionEncoder>());
        }
        ff_OFarm<PortionEncoder> encoderFarm(move(encoders));
        unique_ptr<Concat> concat = make_unique<Concat>(&encoded);
        

        ff_Pipe<> mainPipeline(
            inputStage,
            portionFarm,
            collector,
            coder,
            partitioner,
            encoderFarm,
            concat
        );
        mainPipeline.run_and_wait_end();
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