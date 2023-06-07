#include "huffman.cpp"
#include "utimer.cpp"
#include <ff/ff.hpp>
#include <ff/pipeline.hpp>

#ifndef VERIFY
    #define VERIFY false
#endif

using namespace ff;

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
        

    }
}