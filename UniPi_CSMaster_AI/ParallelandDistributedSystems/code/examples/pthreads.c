#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>
#include <unistd.h>

void * body(void * p) {
  int i = *((int *) p);
  printf("This is thread %d\n", i);
  sleep(1);
  printf("Thread %d terminating now!\n", i);
  return 0;
}

#define MAXT 128

int main(int argc, char **argv) {
  int i;
  int n = atoi(argv[1]);
  pthread_t tids[MAXT]; 

  printf("Creating %d threads \n", n);
  for(i=0; i<n; i++) {
    pthread_create(&tids[i], NULL, body, &i);
  }

  for(i=0; i<n; i++) {
    int * retval = (int *) malloc(sizeof(int)); 
    pthread_join(tids[i], (void **) &retval);
  }
  
  return(0);
  
}