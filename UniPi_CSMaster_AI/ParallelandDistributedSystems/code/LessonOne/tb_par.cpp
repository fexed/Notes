#include <iostream>
#include <fstream>
#include <algorithm>
#include <chrono>
#include <ctime>
#include <vector>
#include <thread>

using namespace std;

// FUNCTION TO TRANSLATE SINGLE CHARACTERS
extern char translate_char(char c);

// USED TO REPRESENT STRING CHUNKS
typedef struct {
  int start;
  int end;
} RANGE;

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

  int    nw       = atoi(argv[2]);  // parallelism degree from command line

  auto compute_chunk = [&text](RANGE range) {   // function to compute a chunk
			 for(int i=range.start; i<range.end; i++) {
			   text[i] = translate_char(text[i]);
			 }
			 return; 
		       };
    
  auto start   = std::chrono::high_resolution_clock::now();
  vector<RANGE> ranges(nw);                     // vector to compute the ranges 
  int m = text.size();
  int delta { m / nw };
  vector<thread> tids;
  
  for(int i=0; i<nw; i++) {                     // split the string into pieces
    ranges[i].start = i*delta;
    ranges[i].end   = (i != (nw-1) ? (i+1)*delta : m); 
  }
  
  for(int i=0; i<nw; i++) {                     // assign chuncks to threads
    tids.push_back(thread(compute_chunk, ranges[i]));
  }
  
  for(thread& t: tids) {                        // await thread termination
    t.join();
  }
  auto elapsed = std::chrono::high_resolution_clock::now() - start;
  auto usec    = std::chrono::duration_cast<std::chrono::microseconds>(elapsed).count();
  // and print time
  cout << "Spent " << usec << " usecs to translate " << filename
       << " in parallel with  " << nw << " threads" << endl; 
  
  
  std::cout << "Writing file to disk" << std::endl;
  // write result to file 
  filename.append(".new");
  ofstream fdo(filename);
  
  fdo << text;
  fdo.close();
  
  return(0);
}
