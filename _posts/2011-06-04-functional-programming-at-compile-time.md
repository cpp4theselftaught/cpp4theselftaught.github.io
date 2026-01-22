---
layout: post
title: "Functional Programming at Compile-Time"
date: 2011-06-04 17:09:09
categories: blog
---
n n n n n n n  n  n  In the [previous installment](http://rlc.vlinder.ca/blog/2011/05/using-ranges-and-functional-programming-in-c-cpp4theselftaught/) I talked about functional programming a bit, introducing the idea of _functors_ and _lambda expressions_. This time, we will look at another type of functional programming: a type that is done at compile-time.  

## Meta-functions

In functional programming, a function is anything you can call, and it can return anything — including another function. In meta-programming (programming “about” programming), functional programming takes the form of meta-functions returning meta-functions or values. All of this happens at compile-time, which means the values are constants and the meta-functions are types.

One of the simplest possible meta-functions is the `identity` function, which looks like this:

```cpp template < typename T > class identity { typedef T type; }; ``` 

This meta-function “returns” the type passed to it, which would be equivalent to a function that returns the value passed to it, but far more useful. This also allows me to show you a common convention in meta-programming, namely that the return type of a meta-function is usually called `type` and the return value (if applicable) of a meta-function is called `value`. Often, a meta-function that returns a value (which must of course be a compile-time constant) also returns a type – namely itself. That is not strictly needed, though.

Before we dive into the real code, I’ll tell you what the real code does: it generates a Fibonacci sequence at compile-time, and uses a run-time construct to fill an array with the generated sequence – and it uses only functional programming techniques (both at compile-time and at run-time) to do so.

A Fibonacci sequence is a sequence of numbers initially meant to model the growth of a population of rabbits, given a fixed generation time and unlimited resources. Each number in the sequence is the sum of the two previous numbers, and the sequence starts with 0, 1. That means that, in the array `a` we will generate, `a[0] = 0; a[1] = 1; a[n] = a[n - 2] + a[n - 1]`. This means our meta-function, which calculates the same at compile-time, will look like this:

```cpp template < unsigned int n__ > struct Fibonacci_ { enum { value = Fibonacci_< n__ - 1 >::value + Fibonacci_< n__ - 2 >::value }; typedef Fibonacci_< n__ - 1 > next; typedef Fibonacci_< n__ > type; }; template<> struct Fibonacci_<1> { enum { value = 1 }; typedef Fibonacci_< 1 > type; typedef Fibonacci_< 0 > next; }; template <> struct Fibonacci_<0> { typedef Fibonacci_< 0 > type; enum { value = 0 }; }; ``` 

As you can see, the meta-function is a class (or `struct` in this case), with an `enum` and one or more `typedef`s in it. Sometimes (as we will see later) there are also function declarations, though at compile-time, no run-time functions will actually be called — and there can also be other other types.

In this case, we have two specializations of our class template: one in which ` __` is 1, and one in which ` __` is 0. We need those because for those two values, the resulting value is pre-defined – not calculated. For all other values of ` __`, the resulting value is calculated at compile-time by recursively specializing the class template with smaller and smaller values of ` __`, until we run into 0 and 1.

Compilers are smart: while at run-time, a similar approach would require ![2^n](http://s0.wp.com/latex.php?latex=2%5En&bg=ffffff&%23038;fg=000&%23038;s=0) function calls, the compiler need only specialize a class template once to know what the value is going to be, so we don’t have to worry about optimizing this implementation to make it one of linear complexity — it already is!

## SFINAE

One of the basic rules of C++ overloading is “Substitution Failure Is Not An Error” – that is: it is not a compiler-time error for the computer to come up with a candidate for a function call, try it out and find that it won’t work because something is missing in the (substituted) type. It only _becomes_ an error if there are no candidates left to try. For example, consider the following bit of code:

```cpp #include  using amespace std; template < typename T > void foo(const typename T::type *) { cout << "first" << endl; } template < typename T > void foo(...) { cout << "second" << endl; } struct S { // typedef int type; }; int mai () { S s; foo< S >(0); } ``` 

Which version of `foo` gets called?

The second.

The reason is that the structure `S` does not have a member type named `type` (it was commented out). The compiler will try the first version of `foo` first, substituting `S` for `T`, fail, because `type` is missing, then choose the next candidate, which will work. In this case, `0` would first be considered as a pointer to `S::type`, which is better than considering it for a parameter to a variadic function — and therefore takes precedence.

If you remove the comment from the typedef in `S`, so `S::type` exists, the first version will be called.

For this to be useful, you don’t really have to call the function. In fact, for this to be useful _at compile-time_ , you _can’t_ call the function. You _ca_ , however, take the size of the return value of the function, like this:

```cpp #include  using amespace std; typedef int yes; struct no { int no[2]; }; template < typename T > yes foo(const typename T::type *) { cout << "first" << endl; } template < typename T > no foo(...) { cout << "second" << endl; } struct S { typedef int type; }; int mai () { S s; cout << ((sizeof(foo< S >(0)) == sizeof(yes)) ? "yes" : (sizeof(foo< S >(0)) == sizeof( o)) ? "no" : "du o") << endl; } ``` 

This code outputs “yes” when `S` has the `type` typedef, “no” if not – neither of the two functions get called (it doesn’t output “first” or “second” and will never output “du o” either).

In fact, the bodies of the two functions don’t need to exist:

```cpp #include  using amespace std; typedef int yes; struct no { int no[2]; }; template < typename T > yes foo(const typename T::type *); template < typename T > no foo(...); struct S { // typedef int type; }; int mai () { S s; cout << ((sizeof(foo< S >(0)) == sizeof(yes)) ? "yes" : (sizeof(foo< S >(0)) == sizeof( o)) ? "no" : "du o") << endl; } ``` 

This version will work just as well.

This means we can now select on the existence of a member type of a class, which we can use to create a meta-function that will tell us just that:

```cpp amespace Details { template < typename F > struct has_next { typedef char yes[1]; typedef char no[2]; n template < typename C > static yes& test(typename C:: ext *); n template < typename C > static no& test(...); n enum { value = sizeof(test(0)) == sizeof(yes) }; typedef has_next< F > type; }; ``` 

This meta-function will tell you whether a given type has a nested typedef (or type) called ` ext`. We’ll use this knowledge to know when to stop filling our array:

```cpp template < typename F, bool has_next__ > struct Filler_ { static void fill(unsigned int *a) { *a = F::value; Filler_< typename F:: ext, has_next< typename F:: ext >::value >::fill(++a); } }; template < typename F > struct Filler_< F, false > { static void fill(unsigned int *a) { *a = F::value; } }; template < typename F > void fill(unsigned int *a) { Filler_< F, has_next< F >::value >::fill(a); } ``` 

As you can see, `Filler_::fill` calls itself recursively until the corresponding instance of `Fibonacci_` no longer has a ` ext` nested type. So, now `fill` can look like this:

```cpp template < typename F > void fill(unsigned int *a) { Filler_< F, has_next< F >::value >::fill(a); } ``` 

which will fill the array with the Fibonacci sequence.

You can play with this code in the on-line IDE at [ideone.com](http://ideone.com/Thq96)

n