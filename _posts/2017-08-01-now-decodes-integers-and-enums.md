---
layout: post
title: "now decodes integers and enums"
date: 2017-08-01 12:08:41
categories: blog
---
n 
    
    
    ow decodes integers and enums
    
    Had a few minutes to kill.nI decided on a large integer representation here, so for integers I'llnjust pass the raw bytes up to the next layer.nFor enums, the representation of choice is int, so that's what I wentnwith.nOf course, if someone decides to pass key as integers (which theynquite often would) they'll have to know how to handle those bytesncorrectly (sign extension being the most likely problem they might ru
    
    into).