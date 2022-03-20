#include <stdlib.h>
#include <iostream>
#include <vector>
#include <future>
#include <functional>

using namespace std;

vector<float> map(vector<float> v, int mode, function<float(float)> fun, int pardegree) {
  int n = v.size();

  if (mode == 0) {  // block
    int n_per_block = n/pardegree;

    int n_processed = 0;
    while (n_processed < n_per_block) {  // each element of block to corresponding worker
      vector<future<float>> tids(pardegree);
      for (int j = 0; j < pardegree; j++) {  // create the threads
        cout << "\t\t" << n_processed + (j*n_per_block) << "->" << j << endl;
        tids[j] = async(launch::async, fun, v[n_processed + (j*n_per_block)]);
      }
      for (int j = 0; j < pardegree; j++) {  // join the threads
        v[n_processed + (j*n_per_block)] = tids[j].get();
      }
      n_processed++;
      cout << "\t\tWork done: " << n_processed*pardegree << endl;
    }
    if (n_processed*pardegree < n) {  // handle the remaining trailing elements
      int remaining = n - (n_processed*pardegree);
      int remain_start = (n_processed*pardegree);
      vector<future<float>> tids(pardegree);
      for (int j = 0; j < remaining; j++) {  // create the threads
        cout << "\t\t" << remain_start+j << "->" << j << endl;
        tids[j] = async(launch::async, fun, v[remain_start+j]);
      }
      for (int j = 0; j < remaining; j++) {  // join the threads
        v[remain_start+j] = tids[j].get();
      }
      cout << "\t\tWork done: " << n_processed*pardegree + remaining << endl;
    }
  } else {  // cyclic
    int work_done = 0;
    while(work_done < n) {  // while there are elements left
      vector<future<float>> tids(pardegree);
      int curr = work_done;
      for (int j = 0; j < pardegree; j++) {  // create the threads
        if (j+curr >= n) break;  // to not go out of bounds
        cout << "\t\t" << j+work_done << "->" << j << endl;
        tids[j] = async(launch::async, fun, v[j+work_done]);
      }
      for (int j = 0; j < pardegree; j++) {  // join the threads
        if (j+curr >= n) break;
        v[j+curr] = tids[j].get();
        work_done++;
      }
      cout << "\t\tWork done: " << work_done << endl;
    }
  }

  return v;
}

int main(int argc, char** argv) {
  vector<float> test_vector;
  function<float(float)> test_function = [](float n)->float{return n + 0.1f;};
  int mode = atoi(argv[1]);
  int n_threads = atoi(argv[2]);
  int n_elements = atoi(argv[3]);

  for (int i = 0; i < n_elements; i++) test_vector.push_back((float) i);
  cout << "Original" << endl;
  for (int i = 0; i < test_vector.size(); i++) cout << i << ".\t" << test_vector[i] << endl;

  vector<float> results = map(test_vector, mode, test_function, n_threads);
  cout << "Results" << endl;
  for (int i = 0; i < results.size(); i++) cout << i << ".\t" << results[i] << endl;

  return 0;
}
