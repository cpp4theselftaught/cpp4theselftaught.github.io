---
layout: post
title: "At a few simple types to the encoder"
date: 2017-08-15 00:08:42
categories: blog
---
n 
    
    
    At a few simple types to the encoder
    
    Adding simple types, such as booleans and end-of-contents, is very easynwith this approach: as long as the output iterator is updated bynanything that writes to the output we simply push whatever we needninto the output by writing to it.
    
    Note that an output iterator should be smart enough to know when itncan't write anymore: as back_inserter will do nicely; a pointer into anfixed-size array is dangerous.
    
    Caveat emptor, as the Romans used to say...