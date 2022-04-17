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

static bool is_prime(int n) {
  if (n <= 3) return n > 1; // 1 is not prime !
  if (n % 2 == 0 || n % 3 == 0) return false;
  for (int i = 5; i * i <= n; i += 6) {
    if (n % i == 0 || n % (i + 2) == 0)
    return false;
  }
  return true;
}

int main(int argc, char* argv[]) {
  return 0;
}
