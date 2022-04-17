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
  auto f = [](float x) { return sqrt(x); };

  promise<float> pfx;

  auto fx = [&](float x) {
    auto res = f(x);
    pfx.set_value(res);  // return as side effect on the promise
    return;
  };

  // get the promise future
  auto futures = pfx.get_future();

  // build the task as always, but instead binding the simple function f
  // we use the function that sets the promise value
  // ideally stored an popped from a queue...
  auto task = bind(fx, 2.0);

  task();

  cout << "Result: " << futures.get() << endl;

  return 0;
}
