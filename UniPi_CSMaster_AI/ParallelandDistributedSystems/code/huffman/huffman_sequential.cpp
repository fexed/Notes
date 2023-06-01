#include "huffman.cpp"
#include "utimer.cpp"

int main(int argc, char **argv) {
    if (argc != 2) {
        cout << "Usage: " << argv[0] << " <filename>" << endl;
        return -1;
    }

    string text = readFile(argv[1]);
    if (text == "") return -2;
    
    vector<char> items;
    vector<int> frequencies;
    map<char, string> codes;
    int list[MAX_HEIGHT];
    int top = 0;
    int size = 0;
    string encoded;

    {
        utimer tseq("Huffman codes sequential");

        readFileData(text, items, frequencies);

        size = items.size();
        auto root = buildHuffmanTree(items, frequencies, size);

        generateCodes(root, list, top, codes);
        encoded = encodeFile(text, codes);
    }

    return 0;
}