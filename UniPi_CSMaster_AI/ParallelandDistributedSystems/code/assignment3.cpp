#include <stdlib.h>
#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <atomic>
#include <barrier>
#include "utimer.cpp"

using namespace std;

// initialize a vector with random numbers
void vector_random_init(vector<int>& v, int max, int seed) {
  srand(seed);
  for (auto &e: v) e = rand() % max;
  return;
}

void vector_print(string text, vector<int>& v) {
  cout << text << ": ";
  for (auto &e: v) cout << e << " ";
  cout << endl;
  return;
}

// sequential odd-even sort
int odd_even_sort_seq(vector<int>& v) {
  bool sorted = false;
  int n_items = v.size();
  int iter = 0;

  while(!sorted) {
    iter++;
    sorted = true;

    // odd phase
    for (int i = 1; i < n_items-2; i += 2) {
      if (v[i] > v[i+1]) {
        auto temp = v[i];
        v[i] = v[i+1];
        v[i+1] = temp;
        sorted = false;
      }
    }

    // even phase
    for (int i = 0; i < n_items-1; i += 2) {
      if (v[i] > v[i+1]) {
        auto temp = v[i];
        v[i] = v[i+1];
        v[i+1] = temp;
        sorted = false;
      }
    }
  }

  return iter;
}

// parallel odd-even sort
int odd_even_sort_par(vector<int>& v, int nw) {
  atomic<bool> sorted;
  sorted = false;
  // [&] = access everything by reference from the outside environment
  barrier barrier_a(nw, [&]() { sorted = true; return; });
  barrier barrier_b(nw, [&]() { return; });
  // need barriers between odd and even steps because the last element of a
  // chunk is compared to the first of the next chunk, which is of the next
  // worker. If we don't wait then we risk interference between workers

  vector<pair<int, int>> chunks(nw);
  auto n_items = v.size();
  auto d = n_items/nw; // assuming it's a multiple, e.g. n_items = 2^k
  for (int i = 0; i < nw; i++) {
    auto start = i*d;
    auto stop = (i == (nw - 1) ? n_items : d*(i+1));
    chunks[i] = make_pair(start, stop);
  }
  atomic<int> global_iters;
  global_iters = 0;

  auto body = [&](int thread_id) {
    auto start = chunks[thread_id].first;
    auto stop = chunks[thread_id].second;
    auto last = (thread_id == (nw - 1));
    if (last) stop = chunks[thread_id].second - 1;
    auto iters = 0;

    while(!sorted) {
      iters++;

      // odd step
      auto localsorted = true;
      for (int i = start + 1; i < stop; i += 2) {
        if (v[i] > v[i+1]) {
          auto temp = v[i];
          v[i] = v[i+1];
          v[i+1] = temp;
          localsorted = false;
        }
      }
      // wait for all the workers
      barrier_a.arrive_and_wait();

      // even step
      // global sorted is true due to barrier_a
      for (int i = start; i < stop; i += 2) {
        if (v[i] > v[i+1]) {
          auto temp = v[i];
          v[i] = v[i+1];
          v[i+1] = temp;
          localsorted = false;
        }
      }

      //wait for all the workers
      // if (sorted && !localsorted)
      // Given that it's an AND, if the first item is false the second item will
      // not be evaluated. So we evaluate "sorted" as a second item in order to
      // reduce the overhead of the many threads requesting the same variable
      if (localsorted == false) // update global sorted only there're changes
        if(sorted)
          sorted = false;
      barrier_b.arrive_and_wait();
      //next iteration
    }
    global_iters = iters; // every thread makes the same number of iterations
    return;
  };

  // threads creation
  vector<thread*> thread_ids(nw);
  for (int i = 0; i < nw; i++) thread_ids[i] = new thread(body, i);
  // wait for them
  for (int i = 0; i < nw; i++) thread_ids[i]->join();

  return global_iters;
}

int main(int argc, char** argv) {
  if (argc == 1) {
    cout << "Usage: " << argv[0] << " seed max n_items debug [nw]" << endl;
  }

  int seed = atoi(argv[1]); // seed for random number generation
  int max = atoi(argv[2]); // max value in the vector
  int n_items = atoi(argv[3]); // length of the vector
  int dbg = (atoi(argv[4]) == 0 ? false : true); // debug flag, if true print
  int nw = (argc == 6 ? atoi(argv[5]) : 1); // par degree, default 1
  long t1, t2, iters;

  vector<int> v(n_items);
  vector_random_init(v, max, seed);
  if(dbg) vector_print("Init", v);

  {
    utimer tseq("Seq", &t1);
    iters = odd_even_sort_seq(v);
  }
  cout << "Sorted in " << iters << " iterations" << endl;
  cout << "A single iteration took on average " << t1 / iters << " usecs" << endl;
  if(dbg) vector_print("Seq odd even sort", v);
  cout << "Seq odd even sort " << ((is_sorted(v.begin(), v.end())) ? "works!" : "error.") << endl << endl;

  vector_random_init(v, max, seed);
  {
    utimer tthread("Par", &t2);
    iters = odd_even_sort_par(v, nw);
  }
  cout << "Sorted in " << iters << " iterations" << endl;
  if(dbg) vector_print("Par odd even sort", v);
  cout << "Par odd even sort " << ((is_sorted(v.begin(), v.end())) ? "works!" : "error.") << endl << endl;

  cout << "Speedup with " << nw << " workers is " << ((float) t1)/((float) t2) << endl;
  return 0;
}
