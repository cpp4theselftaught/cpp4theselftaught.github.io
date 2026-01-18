---
layout: post
title: "Encode and decode sequences and sets"
date: 2017-08-29 17:28:35
categories: blog
---
n 
    
    
    Encode and decode sequences and sets
    
    Decoding sequences and sets is pretty much a question of trying to keepntrack of where you are in the encoded sequence or set (the onlyndifference between the two being that the order in a sequence isnsignificant whereas it isn't in a set). Once you run out of input octetsnfor the sequence or set, you're done with it. At this level, we don't
    
    eed to know what was expected in terms of the contents of the sequencenor set.nHence, we have a simple pair of stacks: one for the type (sequence ornset) and one for the length of the sequence or set being decoded. Wenallow the stack size to be configured, but the default (16) seemsnreasonable to me. Whenever we decode a sequence or set, we simply pushnthe remaining octets for that sequence or set, and its type, onto thenstacks and wait for them to run out. Because DER doesn't supportnindeterminate lengths, that's all we need to do. If the length of thensequence and the length of the contents don't match up, that willninevitably result in a decoding error. That also addresses then"syntactic poison" Adam (@jadamcrain) pointed out i
    
    https://twitter.com/jadamcrain/status/891984403706130432
    
    For the encoder, things are slightly more painful: because DER doesn'tnallow for indeterminate lengths, we have to know the length of whatevernit is we're encoding, which in the case of a sequence depends on thencontents of that sequence. The only way I can deal with that at thenmoment is to pretend whoever is calling the encoder will encode into anvector or buffer of some sort, and be able to pass us the iterators intonthat vector or buffer so we can insert it into whatever it is we'renencoding into. This makes sense w.r.t. the way most of these things arengenerally structured, but it does impose a serious limitation on whoevernwould end up using this code.
    
    Now for some code generation.