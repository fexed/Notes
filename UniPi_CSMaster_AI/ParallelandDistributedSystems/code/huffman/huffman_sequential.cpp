#include "huffman.cpp"
#include "utimer.cpp"

int main(int argc, char **argv) {
    ARG_CHECK

    string text = readFile(argv[1]);
    if (text == "") return -2;

    vector<char> items;
    vector<int> frequencies;
    map<char, string> codes;
    int list[MAX_HEIGHT];
    int top = 0;
    int size = 0;
    string encoded;
    string decoded;

    {
        utimer tseq("Huffman codes sequential");

        readFileData(text, items, frequencies);

        size = items.size();
        auto root = buildHuffmanTree(items, frequencies, size);

        generateCodes(root, list, top, codes);
        encoded = encodeText(text, codes);
    }

    {
        utimer decode("Decoding text");
        decoded = decodeText(encoded, codes);
    }

    if (decoded == text) {
        cout << "Verified!" << endl;
    } else {
        cout << "Encoding not verified..." << endl;
    }

    return 0;
}