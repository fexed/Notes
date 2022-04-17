all: assignment1 assignment2 assignment3 assignment4 assignment5 assignment6

assignment1: assignment1_threads.cpp assignment1_async.cpp
	g++ -pthread assignment1_threads.cpp -o assignment1_threads
	g++ -pthread assignment1_async.cpp -o assignment1_async

assignment2: assignment2.cpp
	g++ -pthread assignment2.cpp -o assignment2

assignment3: assignment3.cpp utimer.cpp
	g++-11 -pthread -std=c++20 assignment3.cpp -o assignment3

assignment4: assignment4.cpp assignment4_packagedtasks.cpp
	g++ -O3 -pthread -std=c++20 assignment4.cpp -o assignment4
	g++ -O3 -pthread -std=c++20 assignment4_packagedtasks.cpp -o assignment4_packagedtasks

assignment5: assignment5.cpp
	g++ -O3 -pthread -fopenmp -std=c++20 assignment5.cpp -o assignment5

assignment6: assignment6.cpp
	g++ -O3 -pthread -std=c++20 assignment6.cpp -o assignment6

clean:
		rm -f assignment1_async assignment1_threads assignment2 assignment3 assignment4 assignment4_packagedtasks assignment5 assignment6

.PHONY: clean, all
