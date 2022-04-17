#include <iostream>
#include <thread>
#include <chrono>

using namespace std::literals::chrono_literals;

#include <omp.h>

void inc(int& i) {
  auto temp = i;
  temp++;
  std::this_thread::sleep_for(10ms);
  i = temp;
  return;
}

int main(int argc, char * argv[]) {

  int i = 0;
  
  auto nw = 1;
  if (argc != 1) nw = atoi(argv[1]);

#pragma omp parallel num_threads(nw)
  {
    //#pragma omp atomic
    i += 1;
  }

  std::cout << "Eventually i = " << i << std::endl; 
  return(0);
}
