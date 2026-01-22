---
layout: post
title: "finish encoding length, octet string"
date: 2017-08-14 12:54:04
categories: blog
---
n 
    
    
    finish encoding length, octet string
    
    What better way to use a lunch break than to eat a nice salad and codensomething on your phone?
    
    Integer can now compact itself to its minimal representation bynremoving leading bytes of nine consecutive bits are zero or there arenonly eight bits and they're all zero; or if the integer is signed and
    
    one consecutive bits are one. The latter ca
    
    ot happen if the formernhas been true, so I check one after the other.
    
    Encoding the length is pretty straightforward once integers ca
    
    compact themselves.