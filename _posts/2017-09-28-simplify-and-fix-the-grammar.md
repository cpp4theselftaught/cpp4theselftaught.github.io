---
layout: post
title: "Simplify and fix the grammar"
date: 2017-09-28 17:29:53
categories: blog
---
n 
    
    
    Simplify and fix the grammar
    
    The parser generated from the grammar parses everything into a tree, sonI've run it against a real ASN.1 schema (using ANTLR's grun) and fixednit where fixes were needed.
    
    I've also simplified it a bit to flatten the generated parse tree, whichnwill make our job parsing it quite a bit easier.