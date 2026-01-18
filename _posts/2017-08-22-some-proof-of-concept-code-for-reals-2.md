---
layout: post
title: "Some proof-of-concept code for reals"
date: 2017-08-22 23:34:28
categories: blog
---
n 
    
    
    Some proof-of-concept code for reals
    
    Decoding reals needs some refactoring: while I've been reading up o
    
    IEEE-754 representation and the standard C++ functions for floatingnpoint types (and confirming that you should avoid touching this stuff ifnyou can) I've come to the conclusion that writing this part of the codenon a tablet or phone is probably not going to lead anywhere, so Indecided to pull out my laptop and get some code ru
    
    ing.
    
    The Details::Integer class compiles and runs - at least as far as thisnproof of concept is concerned. The POC consists of a brand newnimplementation of dissecting and building floating point values (from orninto double, resp.). I've tested it against an independentnimplementation (the calculator on my phone) and arrived at thenconclusion that at least for the two values I've tried so far, it isncorrect. That leads me to believe the method itself is correct as well.
    
    In this commit, we also add the dependencies we'll be working with fromnhere on out: CMake for building (and my cmake submodule for the sharednconfiguration stuff) and the exceptions library with its support for myncontract-theory macros (pre-conditions, invariants, etc.).
    
    I will use the two new functions in the encoder and decoder, replacingnpart of what's there now.