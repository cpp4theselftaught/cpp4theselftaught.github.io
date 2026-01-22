---
layout: post
title: "Optimization by puzzle"
date: 2014-09-04 22:17:43
categories: blog
---
Given a `query` routine that takes a name and may return several, write a routine that takes a single name and returns a set of names for which each of the following is true: 

  1. For each name in the set, `query` has been called exactly once.
  2. All the results from the calls to `query` are included in the set
  3. the parameter to the routine is not included in the set

You may assume the following: 

  1. Calls to `query` are idempotent[1](http://rlc.vlinder.ca/blog/2014/09/optimization-by-puzzle/#footnote_0_3274 "so you really do need to call them only once").
  2. There is a finite number of values for names.
  3. Names are less-than-comparable value-types (i.e. you can store them in an `std::set`) and are not expensive to copy
  4. `query` results never contain their argument[2](http://rlc.vlinder.ca/blog/2014/09/optimization-by-puzzle/#footnote_1_3274 "i.e. for the case at hand, we’re querying a directed acyclic graph, so our first argument will never be seen in any of the query results, although any given value may appear more than once in query results")

This is almost exactly the problem I had to solve recently: a tool was taking several minutes to perform a routine task that, in my opinion, should take milliseconds. Several other issues were involved as well, but this one has the bonus of being fun.

I should make this an interview question.

The way this ends up working is as follows:

  1. We create three sets: one for the `results`, one for the things we’ve `checked` and one for the things that remain `to_check`.
  2. We insert the value we got as a parameter in the `to_check` set.
  3. As long as there are things left to check: 
     1. run `query` for each value in `to_check`
     2. insert the results from the query in the `results` set
     3. After iterating over each of the values, insert the values from `to_check` into the `checked` set,
     4. clear the `to_check` set
     5. fill `to_check` with the set difference between the `results` and the `checked` sets

Or, in C++:

```cpp template < typename T, typename F > set< T > foo(T t, F query) { set< T > results; set< T > checked; set< T > to_check; to_check.insert(t); n do n { for (typename set< T >::const_iterator check(to_check.begi ()); check != to_check.end(); ++check) { typename F::result_type query_results(query(*check)); results.insert(query_results.begi (), query_results.end()); } checked.insert(to_check.begi (), to_check.end()); to_check.clear(); set_difference(results.begi (), results.end(), checked.begi (), checked.end(), inserter(to_check, to_check.end())); } while (!to_check.empty()); retur results; } ``` 

Insertion into a set is ![O\(\\lg{n}\)](http://s0.wp.com/latex.php?latex=O%28%5Clg%7Bn%7D%29&bg=ffffff&%23038;fg=000&%23038;s=0) so lines 43 and 45 are both ![O\(n\\lg{n}\)](http://s0.wp.com/latex.php?latex=O%28n%5Clg%7Bn%7D%29&bg=ffffff&%23038;fg=000&%23038;s=0). Line 46 should be ![O\(c\)](http://s0.wp.com/latex.php?latex=O%28c%29&bg=ffffff&%23038;fg=000&%23038;s=0) but is probably ![O\(n\)](http://s0.wp.com/latex.php?latex=O%28n%29&bg=ffffff&%23038;fg=000&%23038;s=0). Line 47 is ![O\(n\)](http://s0.wp.com/latex.php?latex=O%28n%29&bg=ffffff&%23038;fg=000&%23038;s=0) so the whole things boils down to ![O\(n\\lg{n}\)](http://s0.wp.com/latex.php?latex=O%28n%5Clg%7Bn%7D%29&bg=ffffff&%23038;fg=000&%23038;s=0) complexity.

In order to play with the code a bit, I put it on GitHub as a Gist, with a test case (Query fails if you call it more than once with the same value): 

  1. so you really do need to call them only once
  2. i.e. for the case at hand, we’re querying a directed acyclic graph, so our first argument will never be seen in any of the `query` results, although any given value may appear more than once in `query` results