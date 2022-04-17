#include <iostream>

#include <omp.h>

int main(int argc, char * argv[]) {
  

  if(argc != 1) {
    auto nw = atoi(argv[1]);  
#pragma omp parallel num_threads(nw)
    {
      std::cout << "This is thread " << omp_get_thread_num() << " of "
		<< omp_get_num_threads() << std::endl;
    }
  } else {
#pragma omp parallel
    {
      std::cout << "This is thread " << omp_get_thread_num() << " of "
		<< omp_get_num_threads() << std::endl;
    }
  }
  return(0);
}
