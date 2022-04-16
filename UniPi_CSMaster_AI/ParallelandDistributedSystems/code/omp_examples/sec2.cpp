#include <iostream>
#include <atomic>
#include <chrono>
#include <thread>

using namespace std::literals::chrono_literals;

#include <omp.h>

std::atomic<int> presenceBit;
std::atomic<int> consumedBit;

int buffer;

int main(int argc, char * argv[]) {

  presenceBit = 0;
  consumedBit = 0;
  buffer = 0;
  
  auto delay = 10s;
  auto nw = 1; 
  if(argc!=1) nw = atoi(argv[1]);
  const int n = 4;
  
#pragma omp parallel num_threads(nw)
  {
#pragma omp sections
    {
#pragma omp section
      {
	
	std::cout << "This is the producer section, it is thread "
		  << omp_get_thread_num() << " of "
		  << omp_get_num_threads() << std::endl;
	for(int i=0; i<n; i++) {
	  std::cout << "Waiting buffer free to send ... " << std::endl;
	  while(consumedBit == 0) { std::this_thread::sleep_for(1ms); }
	  std::cout << "Producing item to fill buffer" << std::endl; 
	  std::this_thread::sleep_for(delay);
	  buffer = i;
	  consumedBit = 0;
	  presenceBit = 1;
	  
	  std::cout << "Sent!" << std::endl; 
	}
	
      }
#pragma omp section
      {
	std::cout << "This is second section, thread "
		  << omp_get_thread_num() << " of "
		  << omp_get_num_threads() << std::endl;
	
	consumedBit = 1; // ask for first buffer ... 
	
	for(int i=0; i<n; i++) {
	  std::cout << "Waiting for buffer full to receive ..." << std::endl;
	  while(presenceBit == 0) { std::this_thread::sleep_for(1ms); }
	  std::cout << "Received " << buffer << std::endl;
	  presenceBit = 0;
	  consumedBit = 1;
	}
      }
    } // end sections
  } // end parallel
  
  std::cout << "Both sections terminated ... " << std::endl;
  return(0);
}
