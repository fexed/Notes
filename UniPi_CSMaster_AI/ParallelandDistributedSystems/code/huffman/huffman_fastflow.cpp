#include "huffman.cpp"
#include "utimer.cpp"
#include <ff/ff.hpp>
#include <ff/pipeline.hpp>

#ifndef MAX_THREADS
    #define MAX_THREADS 100
#endif
#ifndef VERIFY
    #define VERIFY false
#endif
#define PORTION_SIZE 1000

using namespace ff;

struct InputStage: ff_node_t<string, string> {
    string text;

    InputStage(const string& param) : text(param) {}

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

    PortionWorkerData* svc(string* portion) {
        PortionWorkerData* data = new PortionWorkerData();
        readFileData(*portion, data->items, data->frequencies);
        free(portion);
        ff_send_out(data);

        return GO_ON;
    }
};

struct FarmCollector: ff_node_t<PortionWorkerData, PortionWorkerData> {
    PortionWorkerData data;

    int svc_init() {
        data = PortionWorkerData();
        return 0;
    }

    PortionWorkerData* svc(PortionWorkerData* portionData) {
        for (unsigned int j = 0; j < portionData->items.size(); j++) {
            std::vector<char>::iterator itr = std::find(data.items.begin(), data.items.end(), portionData->items[j]);
            if (itr != data.items.cend()) {
                data.frequencies[std::distance(data.items.begin(), itr)] += portionData->frequencies[j];
            } else {
                data.items.push_back(portionData->items[j]);
                data.frequencies.push_back(portionData->frequencies[j]);
            }
        }
        free(portionData);

        return GO_ON;
    }
};

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
    string decoded;

    {
        utimer tfastflow("Huffman codes fastflow");
        
        vector<unique_ptr<ff_node>> portionFarmWorkers;
        for (int i = 0; i < MAX_THREADS; i++) {
            portionFarmWorkers.push_back(make_unique<FarmWorker>());
        }
        ff_Farm<PortionWorkerData> portionFarm(move(portionFarmWorkers));

        ff_Pipe<> pipeline(
            make_unique<InputStage>(*text),
            portionFarm,
            make_unique<FarmCollector>()
        );

        pipeline.run_and_wait_end();
    }
    return 0;
}