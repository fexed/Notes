#include <stdio.h>
#include <stdlib.h>
#include <time.h>

using namespace std;

//restrict means that r do not overlap a and b
void vecaddGPU(float *r, float *a, float *b, int n) {
	#pragma acc kernels loop copyin(a[0:n], b[0:n]) copyout(r[0:n])
	for (int i = 0; i < n; i++) r[0] = a[i] + b[i];
}

// note that the GPU memory is managed automatically and not explicitly by the programmer
int main(int argc, char* argv[]) {
	int n; // vector length
	float * a, * b, * r, * e; // inputs, output and expected vectors
	int i, errs;

	if (argc > 1) n = atoi(argv[1]);
	else n = 100000; // default vector length
	if (n <= 0) n = 100000;

	// allocate vectors on the CPU
	a = (float*) malloc(n*sizeof(float));
	b = (float*) malloc(n*sizeof(float));
	r = (float*) malloc(n*sizeof(float));
	e = (float*) malloc(n*sizeof(float));
	// populate vectors
	for (i = 0; i < n; i++) {
		a[i] = (float) i+1;
		b[i] = (float) 1000*i;
	}

	// compute on the GPU
	vecaddGPU(r, a, b, n);

	// compute on host to compare
	clock_t start = clock();
	for (i = 0; i < n; i++) e[i] = a[i] + b[i];
	clock_t stop = clock();
	printf("Seq time is: %f\n", ((double) (stop - start)/CLOCKS_PER_SEC));

	//compare results
	errs = 0;
	for (i = 0; i < n; i++) {
		if (r[i] != e[i]) errs++;
	}

	printf("%d errors found\n", errs);
	return errs;
}
