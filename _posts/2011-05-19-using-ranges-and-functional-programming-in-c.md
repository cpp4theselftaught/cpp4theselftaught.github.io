---
layout: post
title: "Using Ranges and Functional Programming in C++"
date: 2011-05-19 21:47:12
categories: blog
---
n n n n n n n  n  n  C++ is a very versatile language. Among other things, you can do generic meta-programming and functional programming in C++, as well as the better-known facilities for procedural and object-oriented programming. In this installment, we will look at the functional programming facilities in the now-current C++ standard (C++03) as well as the upcoming C++0x standard. We will look at what a _closure_ is and how to apply one to a range, but we will first look at some simpler uses of ranges — to warm up.  
  
If you look at the current version of Chausette, in the code for episode 28, you will find this:

```cpp int mai (int argc, const char **argv) { Applicatio ::Arguments arguments(argc); std::copy(argv, argv + argc, arguments.begi ()); Application applicatio ; try { application.ru (arguments); } catch (...) { std::cerr << "An error occurred" << std::endl; } } ``` 

On line 4 of this listing, you can see our first use of a range: using `copy`, we copy the range of arguments passed to the application into the `arguments` vector.[1](http://rlc.vlinder.ca/blog/2011/05/using-ranges-and-functional-programming-in-c-cpp4theselftaught/#footnote_0_1399 "Note that this is not functional programming \(yet\), but in order to understand how functional programming is thought of in \(current\) C++, it is important to understand how ranges work.") The range that contains all the arguments is `argc` in size (which is why the vector is initialized to contain `argc` elements) and starts at `argv`. This same approach to ranges works for all C-style arrays: the `begi ` ing of the range points at the first element, the `end` of the range points one past the last element. We note a range like this: `[begin, end)`. Using `begi ` and `end` in this ma er works for STL containers as well, and is the basic premise for all STL algorithms.

If you look at the code for `std::copy` you'll find something like this[2](http://rlc.vlinder.ca/blog/2011/05/using-ranges-and-functional-programming-in-c-cpp4theselftaught/#footnote_1_1399 "The real code will likely be more complicated because of some optimizations the implementation may do, but the general idea is the same."):

```cpp template < typename InIter, typename OutIter > OutIter copy(InIter begin, InIter end, OutIter result) { for (; begin != end; ++begi ) { *result++ = *begi ; } retur result; } ``` 

So why not implement the loop directly?

There are many reasons not to implement the loop directly in the code. One is the age-old reason of code re-use. It is for that reason that we practice object-oriented programming, that we have libraries of code and that we have functions. We re-use code because that means we don't have to write as much code (laziness is a virtue in this case) and because we only have to debug the code once. If the code is well-written, having debugged it once means we don't even have to look at it ever again.

For those same reasons, C++ has generic template meta-programming, allowing `copy` to be used for any sort of range containing elements of any type - as long as they are **Assignable**. In this case, we've used it to implement copying a range of C-style strings into a vector of C++-style strings but the same code can copy arrays of integers, the contents of STL containers, etc. Note, by the way, that the copy we did here involves an implicit conversion of the C-style string to the C++-style string: we didn't have to provide any extra code for that because the `std::string` constructor allows for implicit conversion of `const char *`.

Let's go a bit further in the code and see what happens in `Server::update`:

```cpp struct Functor { Functor(fd_set &an;_fd_set, bool Socket::* member, int &highest;_fd) : fd_set_(an_fd_set) , member_(member) , highest_fd_(highest_fd) { /* no-op */ } n Functor &operator;()(const Socket &socket;) { if (!(socket.*member_)) { FD_SET(socket.fd_, &fd;_set_); if (highest_fd_ < socket.fd_) highest_fd_ = socket.fd_; } else { /* don't want this one */ } retur *this; } n fd_set &fd;_set_; bool Socket::* member_; int &highest;_fd_; }; ``` n ```cpp fd_set read_fds; FD_ZERO(&read;_fds); std::for_each( sockets_.begi (), sockets_.end(),n Functor(read_fds, &Socket;::read_avail_, highest_fd)); ``` 

In lines 41 through 64, we define the class `Functor`. This class models a function object (a.k.a. a functor) which, once constructed, behaves exactly like a function would, thanks to the overloaded `operator()` \-- the function-call operator.[3](http://rlc.vlinder.ca/blog/2011/05/using-ranges-and-functional-programming-in-c-cpp4theselftaught/#footnote_2_1399 "Of course, I would not ordinarily call this functor Functor, but I had a point to make. Do not, however, call all your functors by the kind of thing they are -- name them according to their functionality, as you would \(should\) any other chunk of code.") In line 137[4](http://rlc.vlinder.ca/blog/2011/05/using-ranges-and-functional-programming-in-c-cpp4theselftaught/#footnote_3_1399 "135 in the actual code in Git"), the function-object is constructed and is subsequently called for each object in the `sockets_` list, meaning that for each of those objects, the function-call operator of the `Functor` class is called.

This is functional programming, as allowed by C++03 -- the current standard for C++.

Note that there's a wee bit of magic here: in order to allow us to use the same functor for each `fd_set` we mean to set up, we pass a _pointer to a boolean member_ of the `Socket` structure that will be checked in the function-call operator. That is what `bool Socket::* member_` means: `member_` is a pointer to a member of `Socket` that has `bool` type. In C++0x, we won't need to go to so much trouble: we will be able to use _lambda expressions_.

Lambda expressions are a concise way to create a functor class by just defining three things:

  1. what is _captured_ from the definition's environment (in our case, that would be the `fd_set` to work on and the currently-highest file descriptor)
  2. the parameters of the function (just like any other function); and
  3. the body of the function.

These three, together, produce a _closure_ which, if you're not used to it, looks a bit strange. Here's a simple example:

```cpp #include  #include  int mai () { using amespace std; int a[5] = {1, 2, 3, 4, 5}; n for_each(a, a + 5, [](int i){ cout << i << endl; }); } ``` 

In this case, the lambda expression is `[](int i){ cout << i << endl; }`: it doesn't capture anything (`[]` is an empty capture set[5](http://rlc.vlinder.ca/blog/2011/05/using-ranges-and-functional-programming-in-c-cpp4theselftaught/#footnote_4_1399 "I should note that the term ")), takes an integer `i` as parameter and outputs that integer to `cout`.

Now, the lambda expression in this code doesn't actually capture anything. To show how that works, let's capture the array that we loop over:

```cpp #include  #include  int mai () { using amespace std; int a[] = {1, 2, 3, 4, 5}; n auto const f = [=](){ for_each(a, a + (sizeof(a) / sizeof(a[0])), [](int i){ cout << i << endl; }); }; n a[0] = 2; n f(); } ``` 

This lambda expression captures the array `a` by value, so changing the value of one of the integers in the array on line 13 doesn't actually have any effect on the output produced by calling the function on line 15. If we had captured the array by reference, the output would have been different.

There are three versions of this example that you can play with at ideone.com:

  1. [the example](http://ideone.com/v5J6f) code itself`
  2. [a modified version of the example code](http://ideone.com/v8Wsr), in which there is another enclosed lamda expressio 
  3. [another modified version of the example code](http://ideone.com/cMwCa), in which the enclosed lambda expression is returned immediatele

If you have any questions about what you find when you play with that code, feel free to ask.

Lambda expressions are new features of the C++ programming language, but the functional style of programming has existed in C++ since the begi ing: if it is possible to call an object as a function, it is possible to use a functional style of programming. Lambda expressions just make it a bit more interesting. The compilers we’ll want to support for Chausette, however, don’t have most of the features of C++0x (as most compilers don’t) but now that the final draft is out, we’ll add a few notes on C++0x in the installments, when it makes sense to do so.

Once you get a good handle on functional programming, generic template meta-programming becomes a lot easier as it is mostly functional programming, but the program runs at compile-time. We will discuss meta-programming in future installments.

  1. Note that this is not functional programming (yet), but in order to understand how functional programming is thought of in (current) C++, it is important to understand how ranges work.
  2. The real code will likely be more complicated because of some optimizations the implementation may do, but the general idea is the same.
  3. Of course, I would not ordinarily call this functor `Functor`, but I had a point to make. Do not, however, call all your functors by the kind of thing they are -- name them according to their functionality, as you would (should) any other chunk of code.
  4. 135 in the actual code in Git
  5. I should note that the term "capture set" is not mentioned anywhere in the draft standard. I take it to mean the set of actually captured variables, which is the result of the _lambda-capture_ being applied