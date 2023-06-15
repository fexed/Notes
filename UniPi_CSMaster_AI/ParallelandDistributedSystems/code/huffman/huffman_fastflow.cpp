#include "huffman.cpp"
#include "utimer.cpp"
#include <ff/ff.hpp>
#include <ff/pipeline.hpp>
#include <ff/map.hpp>

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
struct PortionWorker: ff_node_t<string, PortionWorkerData> {
    PortionWorkerData* data;

    PortionWorker() {
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

template <typename T>
vector<unique_ptr<ff_node>> prepareWorkers() {
    vector<unique_ptr<ff_node>> workers;
    for (int i = 0; i < MAX_THREADS; i++) {
        workers.push_back(make_unique<T>());
    }
    return workers;
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
    string encoded;
    string decoded;

    {
        utimer tfastflow("Huffman codes fastflow");
        
        // Input stage, partitions the text into portions of PORTION_SIZE length
        unique_ptr<Partitioner> inputStage = make_unique<Partitioner>(*text);

        // Map that gathers data about characters and frequencies of each portion
        vector<unique_ptr<ff_node>> portionFarmWorkers = prepareWorkers<PortionWorker>();
        ff_Farm<PortionWorkerData> portionFarm(move(portionFarmWorkers));

        // Collects data for the sequential stage
        unique_ptr<FarmCollector> collector = make_unique<FarmCollector>();

        // Sequential stage that computes the codes
        unique_ptr<CodesBuilder> coder = make_unique<CodesBuilder>(&codes);

        // Partions the text to be encoded
        unique_ptr<EncoderPartitioner> partitioner = make_unique<EncoderPartitioner>(*text);

        // Map that encodes the text
        vector<unique_ptr<ff_node>> encoders = prepareWorkers<PortionEncoder>();
        ff_OFarm<PortionEncoder> encoderFarm(move(encoders));

        // Concatenates the already ordered encoded portions
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

        auto numbers = getNumberSequence(encoded);
        auto bitString = getBitString(numbers).substr(getPaddingLength(encoded));
        if (check(bitString, decoded)) {
            cout << "Verified!" << endl;
        } else {
            cout << "BitString not verified..." << endl;
        }
        
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