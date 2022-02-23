// local machine 
#include <string>

char translate_char(char c) {

  if(islower(c))
    return(toupper(c));
  else
    return(tolower(c));

}
