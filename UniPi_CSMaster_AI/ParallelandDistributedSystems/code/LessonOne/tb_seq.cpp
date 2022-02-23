#include <iostream>
#include <fstream>
#include <algorithm>

using namespace std;

// FUNCTION TO TRANSLATE SINGLE CHARACTERS
extern char translate_char(char c);

int main(int argc, char * argv[]) {

  std::cout << "Program started" << std::endl;
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
  
  transform(text.begin(), text.end(), text.begin(),
	    translate_char);

  std::cout << "Writing file to disk" << std::endl;
  // write result to file 
  filename.append(".new");
  ofstream fdo(filename);

  fdo << text;
  fdo.close();
  std::cout << "Done ! " << std::endl;
  return(0);
}
