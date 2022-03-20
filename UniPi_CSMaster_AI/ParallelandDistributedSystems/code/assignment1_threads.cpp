#include <iostream>
#include <thread>
#include <atomic>
#include <vector>
#include <chrono>

#define INIT_TIME \
  auto start = chrono::high_resolution_clock::now(); \
  auto elapsed = chrono::high_resolution_clock::now() - start; \
  auto usec = chrono::duration_cast<chrono::microseconds>(elapsed).count();
#define BEGIN_TIME \
  start = chrono::high_resolution_clock::now();
#define END_TIME(prefix, n_threads) \
  elapsed = chrono::high_resolution_clock::now() - start; \
  usec = chrono::duration_cast<chrono::microseconds>(elapsed).count(); \
  cout << prefix << "\t" << usec << " usecs over " << n_threads << " threads" << endl;

using namespace std;

int main(int argc, char** argv) {
  int N_EVENTS = atoi(argv[1]);
  int N_THREADS = atoi(argv[2]);

  INIT_TIME;

  vector<thread*> tids(N_THREADS);

  BEGIN_TIME;

  for (int i = 0; i < N_EVENTS; i++) {
    for (int j = 0; j < N_THREADS; j++) {  // create the threads
      tids[j] = new thread([] (int i) {return;}, j);
    }

    for (int j = 0; j < N_THREADS; j++) {  // join them
      tids[j]->join();
    }
  }

  END_TIME("Raw time", N_THREADS);
  float avg = ((((float) usec) / ((float) N_EVENTS)) / ((float) N_THREADS));
  cout << "Average per thread (fork + join)\t" << avg << "s" << endl;

  return 0;
}
