---
layout: post
title: "encode reals"
date: 2017-08-20 19:25:59
categories: blog
---
n 
    
    
    encode reals
    
    Real encoding is among the more complex encodings in DER. It doesn'tnfollow IEEE-754 at all, so we have to extract the mantissa and thenexponent, in the case of the mantissa decide whether to represent itnin base 2, 8 or 16 and in either case encode the sign and the value.nSubnormal values resolve to zero in the mantissa and can'tnrepresented, so they will hit am assertion on line 175 of this code.
    
    I should note that I heartily dislike floating points for variousnreasons, not least of which quirks like subnormal values, epsilon,nwhacky encodings, etc. Add to that that most, if not all, floatingnpoint values "in the wild" are really either a function of somenirrational number (pi, e, ...), a fraction, or an integer measurementnwith scaling (gain and offset) lossy representations like IEEE-754 ornthis one are really u
    
    ecessary (just store the function, fraction, ornmeasurements in stead).