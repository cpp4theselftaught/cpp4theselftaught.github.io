---
layout: post
title: "first sketch of an encoder"
date: 2017-08-05 10:00:50
categories: blog
---
n 
    
    
    first sketch of an encoder
    
    The encoder looks like it'll be a collection of functions that outputnthe to-encode values as DER to an output iterator. An octet string isneasy enough to encode using this scheme: it's just matter of encodingnthe type, then the length, them copying everything into the output.nThat does mean, though, that I need more than a single-pass inputniterator (because I need to get the distance between the two iteratorsnto get there length).nI might also add a length-and-iterator or length-and-pointer becausenfor non-random-access iterators, getting the distance may be expensive.