#include <iostream>
#include <functional>
#include <vector>
#include <chrono>
#include <optional>
#include <ctime>
#include <future>
#include <queue>
#include <mutex>
#include <cmath>

using namespace std;
using namespace std::literals::chrono_literals;  // for "1ms"

int main(int argc, char* argv[]) {
  if (argc == 1) {
    cout << "Usage: " << argv[0] << " nw m ta tf" << endl;
    return 0;
  }

  int nw = atoi(argv[1]);
  int m = atoi(argv[2]);  // items to be computed
  int ta = atoi(argv[3]);  // interarrival time
  int tf = atoi(argv[4]);  // time to compute the single item

  // protects the queue, global lock to access the queue
  mutex ll;
  // double ended queue that hosts the tasks to be computed
  // packaged tasks are different from binds, return a future that can be asked
  // to know if a task has been computed
  deque<packaged_task<float()>> tasks;
  // used to signal and wait between the 1 writer (inputstream provider) and
  // nw readers that pops the tasks in the queue
  condition_variable cond;
  // used to signal that the tasks have ended
  bool stop = false;

  // executed by the writer, submits the tasks f passed as argument (the bind
  // object)
  auto submit = [&] (packaged_task<float()>& f) {
    { // section where we obtain the unique lock
      unique_lock<mutex> lock(ll);
      tasks.push_back(move(f));  // add to the end of the queue
    }
    cond.notify_one();  // lost if nobody is waiting
  };

  // threads in the pool execute this
  auto body = [&] (int i) {
    while(true) {
      packaged_task<float()> t;
      { // unique lock wait and obtain
        unique_lock<mutex> lock(ll);
        // we wait until the queue is not empty
        // when that happens, the lock is released
        cond.wait(lock, [&]() { return (!tasks.empty() || stop); });
        // get the first task
        if (!tasks.empty()) {
          t = move(tasks.front());  // doesn't remove from the queue
          tasks.pop_front();  // doesn't return anything
        } else if (stop) return;  // body thread finishes
      }
      t();  // and exec it. function of float with no param, must be ouside
    }
  };

  // gets the tf variable as value from the global environment
  auto f = [tf](float x) {
    this_thread::sleep_for(tf * 1ms);  // simulate work
    auto res = sqrt(x);
    //cout << res << endl;  // use the futures as output, see later
    return res;
  };

  auto stop_threadpool = [&]() {
    {
      unique_lock<mutex> lock(ll);
      stop = true;
    }
    cond.notify_all();
  };

  // create the threadpool of nw threads that executes the body but each waits
  // because the queue is empty
  vector<thread> thread_ids(nw);
  for (int i = 0; i < nw; i++) thread_ids[i] = thread(body, i);

  vector<future<float>> futures(m);

  for (int i = 0; i < m; i++) {
    this_thread::sleep_for(ta * 1ms);  // simulate interarrival time
    auto x = (double) i;
    cout << "Task " << x << " arrived" << endl;
    auto fx = (bind(f, x));
    packaged_task<float()> pt(fx);
    futures[i] = pt.get_future();  // store the future
    submit(pt);
  }

  for (int i = 0; i < m; i++) cout << futures[i].get() << " computed" << endl;
  stop_threadpool();  // no more tasks left

  for (int i = 0; i < nw; i++) thread_ids[i].join();  // wait for the finish

  return 0;
}
