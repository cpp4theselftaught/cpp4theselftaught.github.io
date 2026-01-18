---
layout: post
title: "Run-time composed predicates and Code generation"
date: 2013-09-20 18:58:08
categories: blog
---
While working on Arachnida, preparing version 2.2 due out this fall, one of the things we’ll be introducing is a hardened OpenSSL transport-layer-security plug-in, to replace the one we’ve had for the last seven or so years. One of the new features in this plug-in (which is part of Arachnida’s “Scorpion” module) is a much more flexible configuration scheme including the subject of today’s post: run-time composed predicates.

As the name indicates, run-time composed predicates are predicates that are composed at run-time. In this case, we use them for post-co ection validations of the SSL/TLS co ection: the user can plug their own post-co ection validations in and combine them with the ones provided in the library using AND, OR, NOR, NAND, XOR and NOT primitives. Typically, such a composed predicate would look like this:

```cpp configuration.post_co ection_verification_predicate_ = and_( and_( peer_provided_certificate__, fqdn_matches_peer__) , userProvidedPredicate); ``` 

in which `userProvidedPredicate` is a pointer to a user-provided predicate function whereas the other two predicates are included in the library.

The thing is that each of the following will also work:

```cpp // if the peer provided a predicate, assume everything is fine configuration.post_co ection_verification_predicate_ = peer_provided_certificate__; // we accept this only of the FQDN in the peer-provided certificate DOES NOT match the peer's FQDN // THIS IS STUPID - DO NOT DO THIS IN YOUR CODE! configuration.post_co ection_verification_predicate_ = not_(fqdn_matches_peer__); // apply only the user's predicate configuration.post_co ection_verification_predicate_ = userProvidedPredicate; ``` 

The trick here is that the predicate type, `PostCo ectionVerificationPredicate`, is a function-to-pointer type and the functions `and_`, `or_`, `xor_`, ` and_`, ` or_` and ` ot_` each return a function to a “newly created” function.

Of course, C++ does not allow the creation of functions at run-time and, as the call-back is passed to OpenSSL and OpenSSL is written in C, more to the point, neither does C.

As Arachnida is designed to run on industrial control systems and industrial embedded devices, we want to avoid run-time memory allocation if at all possible — and when that’s not possible, we want to control it. In this case, we avoid it by creating an array of pointers to functions, another array of “configurations” for those functions and a function for each position in the array. We do this using a Perl script (because we usually use Perl to generate code and it integrates nicely with our build system).

The following chunk of code is the generation script verbatim — a otated.

First, the usual pre-amble code: for the Perl part, this is invoking the interpreter; for the C++ code, this is including the neccessary headers.

```perl #! /usr/bin/env perl my $name = $0; my $max_predicate_count = 20; print < #include  ``` 

The maximum predicate count is set above, and replicated in the generated C++ source code here. To change it, we currently need to change the script. At some point (probably before version 2.2 of Arachnida is released) this will become a command-line argument to the script.

```perl #define MAX_PREDICATE_COUNT ${max_predicate_count} amespace Scorpion { namespace OpenSSL { namespace Details { namespace { static unsigned int next_predicate_id__ = 0; ``` 

The following is how predicates are allocated: any call to any of the predicate construction functions (`and_`, `or_`, etc.) will call this once, and throw `bad_alloc` if it fails.

```perl unsigned int allocatePredicateID() { if (MAX_PREDICATE_COUNT == next_predicate_id__) throw std::bad_alloc(); retur next_predicate_id__++; } ``` 

The following structure holds the configuration of the “generated” predicate. This is all we need to know for any operator: what the left-hand-side of the expression is, what the right-hand-side is and what operator it is. One operator is unary, all the others are binary. The unary one only uses the `lhs_` member of this structure.

```perl struct PredicateInfon { enum Type { and__n , or__n , xor__n , nand__n , nor__n , not__n }; n Type type_; PostCo ectionVerificationPredicate lhs_; PostCo ectionVerificationPredicate rhs_; }; ``` 

The following is an array of each of these configurations, followed by Perl code to generate each of the functions. I could have used a template to generate these rather than generated code but I find as long as I’m generating code anyway, it makes more sense to just keep generating — especially if there’s no compelling reason to do otherwise.

```perl PredicateInfo predicate_infos__[MAX_PREDICATE_COUNT]; EOF ; for (my $i = 0; $i < $max_predicate_count; ++$i) { print <We can now generate the array of function pointers that the operator/generator code will pick from:

```perl print <and create a function for each operator. Not that the binary operators are all the same for all intents and purposes, so might as well generate those too.

```perl my @keywords = qw/and or nor xor nand/; foreach $keyword (@keywords) { print <A few fun tidbits: the `#line` directives tell the compiler where to look for the code for stepping etc., so if you step through this code you’ll be stepping into Perl!

This approach works for a whole slew of other repetitive code. Generated code, once debugged etc., usually scales pretty well: if I need a thousand of these operators for some reason, I have one constant to change and no other questions to ask (except perhaps why I could possibly need that many predicates!)

I used a very similar approach to translate a dump from the Unicode into C code to parse it: computers are very good at repeating themselves with minor variations in what they’re saying. This is an example of how you can reduce the amount of work you do by making the computer do more.

n