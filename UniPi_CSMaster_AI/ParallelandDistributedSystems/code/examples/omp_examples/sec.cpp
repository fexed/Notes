#include <iostream>
#include <unistd.h>
#include <omp.h>

#include <thread>
#include <chrono>
using namespace std::literals::chrono_literals;

int main(int argc, char * argv[]) {
 
  auto nw = 1; 
  if(argc != 1) nw = atoi(argv[1]);

  srand(getpid());
  #pragma omp parallel num_threads(nw)
    {
#pragma omp sections
      {
#pragma omp section
	{
	  int times = rand() % 32;
	  for(int i=0; i<times; i++) {
	    std::this_thread::sleep_for(100ms);
	    std::cout << "1"; 
          }
	  std::cout << "\nThis is first section, thread " << omp_get_thread_num() << " of "
		    << omp_get_num_threads() << std::endl;
	  
	}
#pragma omp section
	{
	  int times = rand() % 32;
	  for(int i=0; i<times; i++) {
	    std::this_thread::sleep_for(100ms);
	    std::cout << "2"; 
          }
	  std::cout << "\nThis is second section, thread " << omp_get_thread_num() << " of "
		    << omp_get_num_threads() << std::endl;
	}
      } // end sections
    } // end parallel
  return(0);
}
