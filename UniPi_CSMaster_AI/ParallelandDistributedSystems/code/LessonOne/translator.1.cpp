//
// define the function translating a char into another char
// for the sake of simplicity:
// just turns letters capital to small and viceversa,
// loosing some time
//

#include <string>
#include <ctime>
#include <chrono>

void active_delay(int msecs) {
  // read current time
  auto start = std::chrono::high_resolution_clock::now();
  auto end   = false;
  while(!end) {
    auto elapsed = std::chrono::high_resolution_clock::now() - start;
    auto msec = std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
    if(msec>msecs)
      end = true;
  }
  return;
}

auto translate_char(char c) {
  // loose some time in case
  active_delay(1);
  if(islower(c))
    return(toupper(c));
  else
    return(tolower(c));
}
