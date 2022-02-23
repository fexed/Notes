#include <iostream>
#include <fstream>
#include <algorithm>
#include <chrono>
#include <ctime>

using namespace std;

// FUNCTION TO TRANSLATE SINGLE CHARACTERS
extern char translate_char(char c);

int main(int argc, char * argv[]) {
  
  string filename = argv[1];
  
  ifstream fd(filename);   // open input file
  string   text = "";      // text will be accumulated here
  string line;             // used to read
  
  // works under the assumption the text len < str.max_size()
  while(getline(fd,line)) {
    text.append(line);
    text.append("\n");
  }
  fd.close();              // file read completed
  
  std::cout << "File read in memory" << std::endl;
  
  auto start   = std::chrono::high_resolution_clock::now();
  transform(text.begin(), text.end(), text.begin(),
	    translate_char);
  auto elapsed = std::chrono::high_resolution_clock::now() - start;
  auto usec    = std::chrono::duration_cast<std::chrono::microseconds>(elapsed).count();
  // and print time

  cout << "Spent " << usec << " usecs to translate " << filename
       << " sequentially " << endl; 

  std::cout << "Writing file to disk" << std::endl;
  // write result to file 
  filename.append(".new");
  ofstream fdo(filename);

  fdo << text;
  fdo.close();
  std::cout << "Done ! " << std::endl;
  return(0);
}
