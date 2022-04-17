#include <iostream>
#include <chrono>
#include <thread>
#include <omp.h>

using namespace std;
using namespace std::literals::chrono_literals;

void offload(int task, int tw) {
  #pragma omp task
  {
    this_thread::sleep_for(tw * 1ms);
    cout << "Task " << task << " = " << task*task << endl;
  }
  return;
}

int main(int argc, char* argv[]) {
  if (argc == 1) {
    cout << "Usage: " << argv[0] << " nw m ta tw" << endl;
    return 0;
  }

  int nw = atoi(argv[1]);
  int m = atoi(argv[2]);  // items to be computed
  int ta = atoi(argv[3]);  // interarrival time
  int tw = atoi(argv[4]);  // time to compute the single item

  #pragma omp parallel num_threads(nw)
  {
    #pragma omp master
    {
      for (int i = 0; i < m; i++) {
        int task = i;
        this_thread::sleep_for(ta * 1ms);
        offload(task, tw);
      }
    }
    #pragma omp taskwait
  }

  return 0;
}
