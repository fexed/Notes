#include "huffman.cpp"
#include "utimer.cpp"
#include <ff/ff.hpp>
#include <ff/pipeline.hpp>

#ifndef VERIFY
    #define VERIFY false
#endif

using namespace ff;

typedef struct {
    vector<char> items;
    vector<int> frequencies;
} PortionWorkerData;
struct testStage: ff_node_t<PortionWorkerData> {
    PortionWorkerData data;

    int svc_init() {
        data = PortionWorkerData();
        return 0;
    }

    PortionWorkerData* svc(string portion) {
        readFileData(portion, data.items, data.frequencies);

        return &data;
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
        
        vector<unique_ptr<ff_node>> W;
        W.push_back(make_unique<testStage>())
        W.push_back(make_unique<testStage>())
        W.push_back(make_unique<testStage>())
        W.push_back(make_unique<testStage>())

        
    }
}