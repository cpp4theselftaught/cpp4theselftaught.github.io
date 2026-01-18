---
layout: post
title: "parse bit strings"
date: 2017-08-03 06:58:58
categories: blog
---
n 
    
    
    parse bit strings
    
    Because this is a DER decoder, which means sizes must always bendeterminate, we only parse primitive bit strings.nWe essentially ignore the constructed flag, though, as it's redundantnwith the indeterminate length on constructed bit strings and I see nonway for an attacker to exploit setting the flash but not using a
    
    indeterminate length and some encoders might (not unreasonably, butnwrongly nonetheless) always set the flash on bit strings.
    
    Anecdotally, this code was written yesterday, in the car, while mynwife was driving :slightly_smiling_face: