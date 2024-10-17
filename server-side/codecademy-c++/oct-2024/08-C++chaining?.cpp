// ----------------------------------- //
//
// -- C++ Programming -- Print Resulting Variable
//
// ----------------------------------- //

/*
Now that we have outputted a variable and have also outputted things using multiple couts, let’s take a closer look at cout again.

If we have the code below:

*/

int age = 28;

std::cout << "Hello, I am ";
std::cout << age;
std::cout << " years old\n";

/*
Notice how we use quotes around the characters in "Hello, I am " but not in age.

We use quotes when we want a literal string.

We don’t use quotes when we refer to the value of something with a name (like a variable).

So now, is it possible to write the cout statements within a single line?

Yep! You can use multiple << operators to chain the things you want to output.

For the same code above you can also do:

*/

