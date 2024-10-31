// -------------------------------------------- //
//
// -- C++ Programming -- User Input -- 
//
// -------------------------------------------- //

/*
Like we mentioned in the introduction, another way to assign a value to a variable is through user input. A lot of times, we want the user of the program to enter information for the program.

We have cout for output, and there is something called cin that’s used for input!

*/

Like we mentioned in the introduction, another way to assign a value to a variable is through user input. A lot of times, we want the user of the program to enter information for the program.

We have cout for output, and there is something called cin that’s used for input!

/* 
The name cin refers to the standard input stream (pronounced “see-in”, for character input). The second operand of the >> operator (“get from”) specifies where that input goes.

To see how it works, we have to try it with a program.

*/

#include <iostream>

int main() {
  
  int tip = 0;
  
  std::cout << "Enter tip amount: ";
  std::cin >> tip;
  
}

// ------------------------------------------------------------ //

/* 

With chaining --> produce this output --> You paid [tip] dollars.

*/

#include <iostream>

int main() {
  
  int tip = 0;
  
  std::cout << "Enter tip amount: ";
  std::cin >> tip;
  
  std::cout << "You paid " << tip << " dollars. \n";
  
}