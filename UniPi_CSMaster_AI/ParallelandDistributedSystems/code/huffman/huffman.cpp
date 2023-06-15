#include <iostream>
#include <fstream>
#include <vector>
#include <memory>
#include <map>
#include <iomanip>
#include <bitset>

#define MAX_HEIGHT 50

using namespace std;

#define ARG_CHECK \
if (argc != 2) { \
    cout << "Usage: " << argv[0] << " <filename>" << endl; \
    return -1; \
} \

struct Node {
    char value;
    unsigned int frequency;
    shared_ptr<Node> left;
    shared_ptr<Node> right;

    Node(char item, unsigned int freq) :value(item), frequency(freq), left(nullptr), right(nullptr) {}
};

struct MinHeap {
    unsigned int size;
    unsigned int capacity;
    vector<shared_ptr<Node>> list;

    MinHeap(unsigned int cap) : size(0), capacity(cap) {
        list.reserve(capacity);
    }
};

shared_ptr<Node> createNode(char item, unsigned int frequency) {
    return make_shared<Node>(item, frequency);
}

shared_ptr<MinHeap> createMinimumHeap(unsigned int capacity) {
    return make_shared<MinHeap>(capacity);
}

void printMinimumHeap(const shared_ptr<Node>& root, int level = 0, char prefix = ' ') {
    if (!root)
        return;

    printMinimumHeap(root->right, level + 1, '/');

    for (int i = 0; i < level; i++)
        cout << "    ";

    if (prefix != ' ')
        cout << prefix << "----";

    cout << root->value << endl;

    printMinimumHeap(root->left, level + 1, '\\');
}

// perform rotations
void makeMinimumHeap(shared_ptr<MinHeap> minHeap, int index) {
    int smallest = index;
    unsigned int left = 2 * index + 1;
    unsigned int right = 2 * index + 2;

    if (left < minHeap->size && minHeap->list[left]->frequency < minHeap->list[smallest]->frequency) {
        smallest = left;
    }

    if (right < minHeap->size && minHeap->list[right]->frequency < minHeap->list[smallest]->frequency) {
        smallest = right;
    }

    if (smallest != index) {
        swap(minHeap->list[smallest], minHeap->list[index]);
        makeMinimumHeap(minHeap, smallest);
    }
}

shared_ptr<Node> extract(shared_ptr<MinHeap> minHeap) {
    auto tmp = minHeap->list[0];
    minHeap->list[0] = minHeap->list[minHeap->size - 1];
    minHeap->size--;
    makeMinimumHeap(minHeap, 0);

    return tmp;
}

void insert(shared_ptr<MinHeap> minHeap, shared_ptr<Node> node) {
    minHeap->size++;
    int i = minHeap->size - 1;

    while (i > 0 && node->frequency < minHeap->list[(i - 1) / 2]->frequency) {
        minHeap->list[i] = minHeap->list[(i - 1) / 2];
        i = (i - 1) / 2;
    }

    minHeap->list[i] = node;
}

void buildMinimumHeap(shared_ptr<MinHeap> minHeap) {
    int n = minHeap->size - 1;
    int i = (n - 1) / 2;

    for (; i >= 0; i--) {
        makeMinimumHeap(minHeap, i);
    }
}

shared_ptr<MinHeap> createAndBuildMinimumHeap(const vector<char>& items, const vector<int>& frequencies, int size) {
    shared_ptr<MinHeap> minHeap = createMinimumHeap(size);

    for (int i = 0; i < size; i++) {
        minHeap->list.push_back(createNode(items[i], frequencies[i]));
    }

    minHeap->size = size;
    buildMinimumHeap(minHeap);

    return minHeap;
}


shared_ptr<Node> buildHuffmanTree(const vector<char>& items, const vector<int>& frequencies, int size) {
    auto minHeap = createAndBuildMinimumHeap(items, frequencies, size);

    while (minHeap->size != 1) {
        auto left = extract(minHeap);
        auto right = extract(minHeap);

        auto top = createNode('$', left->frequency + right->frequency);

        top->left = left;
        top->right = right;

        insert(minHeap, top);
    }

    return extract(minHeap);
}

bool isLeaf(const shared_ptr<Node>& node) {
    return !(node->left) && !(node->right);
}

void generateCodes(const shared_ptr<Node>& root, int list[], int top, map<char, string>& codes) {
    if (root->left) {
        list[top] = 0;
        generateCodes(root->left, list, top + 1, codes);
    }

    if (root->right) {
        list[top] = 1;
        generateCodes(root->right, list, top + 1, codes);
    }

    if (isLeaf(root)) {
        string code;
        for (int i = 0; i < top; i++) {
            code += to_string(list[i]);
        }
        codes[root->value] = code;
    }
}

void readFileData(string& text, vector<char>& items, vector<int>& frequencies) {  
    if (!text.empty()) {
        for (char ch : text) {
            bool found = false;
            size_t index = 0;
            for (; index < items.size(); index++) {
                if (items[index] == ch) {
                    found = true;
                    break;
                }
            }

            if (found) {
                frequencies[index]++;
            } else {
                items.push_back(ch);
                frequencies.push_back(1);
            }
        }
    }
}

string encodeText(const string& text, map<char, string> codes) {
    string encoded;
    if (!text.empty()) {
        for (char ch : text) {
            encoded += codes[ch];
        }
    }

    return encoded;
}

string decodeText(const string& text, map<char, string> codes) {
    string decoded;

    map<string, char> reverseCodes;

    for (auto const& [ch, code] : codes) {
        reverseCodes[code] = ch;
    }

    if (!text.empty()) {
        string cur = "";
        for (char ch : text) {
            cur += ch;
            if (reverseCodes.find(cur) != reverseCodes.end()) {
                decoded += reverseCodes[cur];
                cur = "";
            }
        }
    }

    return decoded;
}

string readFile(char* filename) {
    ifstream file(filename);
    if (!file) {
        cout << "Cannot open: " << filename << endl;
        return "";
    }
    string fileContent = "";
    string tmpstring = "";
    while (file.good()) {
        getline(file, tmpstring);
        fileContent += tmpstring;
        fileContent += "\n";
    }
    file.close();
    return fileContent;
}

void printCodes(map<char, string>& codes) {
    for (const auto& pair : codes) {
        std::cout << pair.first << " -> " << pair.second << std::endl;
    } 
}

bool check(string original, string decoded) {
    return original.compare(decoded) == 0;
}

int getPaddingLength(const string bitString) {
    const unsigned int numberSize = sizeof(unsigned long long);
    return numberSize - bitString.length() % numberSize;
}

vector<unsigned long long> getNumberSequence(const string bitString) {
    const unsigned int numberSize = sizeof(unsigned long long);
    string paddedString = string(getPaddingLength(bitString), '0') + bitString;
    vector<unsigned long long> numbers;

    for (unsigned int i = 0; i < paddedString.length(); i += numberSize) {
        string block = paddedString.substr(i, numberSize);
        bitset<numberSize> bits(block);
        numbers.push_back(static_cast<unsigned long long>(bits.to_ullong()));
    }

    return numbers;
}

string getBitString(vector<unsigned long long> numbers) {
    const unsigned int numberSize = sizeof(unsigned long long);
    std::string bitString;

    for (const unsigned long long& number : numbers) {
        bitset<numberSize> bits(number);
        string paddedString = bits.to_string();
        bitString += paddedString;
    }

    return bitString;
}