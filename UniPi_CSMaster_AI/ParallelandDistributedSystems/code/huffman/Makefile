seq:
	g++ -O3 -std=c++17 -Wall -pedantic huffman_sequential.cpp -o huffman_seq

threads:
	g++ -O3 -std=c++17 -Wall -pedantic -pthread -DMAX_THREADS=$(NW) huffman_pthread.cpp -o huffman_threads 

fastflow:
	g++ -O3 -std=c++17 -Wall -pedantic -pthread -DMAX_THREADS=$(NW) huffman_fastflow.cpp -o huffman_fastflow