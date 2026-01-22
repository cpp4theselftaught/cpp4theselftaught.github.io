---
layout: post
title: "continue a bit on decoding reals"
date: 2017-08-05 21:59:19
categories: blog
---
n 
    
    
    continue a bit on decoding reals
    
    It's a nice night to be coding on one's phone.
    
    Special real values are now decoded, and the entire value is copiedninto the buffer. Now we need to get the number of octets for thenexponent (which we'll need to check against the octets we actuallynhave) after which we can finish calculating the mantissa.
    
    I've decided on using double to represent reals. I could make thatnconfigurable, but I don't see much of a reason for doing that.
    
    The new Integer class is now used to report the integer value.