---
layout: post
title: "encode bit strings"
date: 2017-08-20 16:06:32
categories: blog
---
n 
    
    
    encode bit strings
    
    Representing a bit string as a pair of iterators and an integer shouldnbe sufficient in almost any case, and add we require (because this isna DER encoder) for the entire bit string to be available, this'll do.
    
    Note, again, that the expected input iterator is a multi-pass inputniterator: we need to be able to calculate the distance between thenbegi
    
    ing and the end of the input range.