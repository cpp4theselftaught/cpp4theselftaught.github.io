---
layout: post
title: "(Fairly) complete ANTLR grammar for ASN.1"
date: 2017-09-27 20:40:24
categories: blog
---
n 
    
    
    (Fairly) complete ANTLR grammar for ASN.1
    
    The grammar was mostly just copied out of X.680 and ANTLRised. To donthis, some minor simplifications were needed removing intermediatenproductions that were probably originally necessary for whateverncompiler compiler the ASN.1 folks used when testing their definitions
    (probably some Yacc variant).
    
    I also had to change the naming convention used for the productions andnlexical tokens: while I usually don't care that much about namingnconventions, they exist for parsing purposes (our brains are simplynbetter at parsing than most computer-generated recognizers). ANTLR hasncertain rules about what productions and tokens should look like, so we
    
    eed to follow those rules if we want to use ANTLR.
    
    I'll also only be implementing X.680, so any production that referencednthigns that are not part of X.680 are (partly) removed from the grammar.nI've further removed stuff that I either won't implement or would resultnin ambiguities or redundancies in the grammar.