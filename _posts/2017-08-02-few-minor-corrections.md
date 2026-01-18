---
layout: post
title: "few minor corrections"
date: 2017-08-02 08:16:25
categories: blog
---
n 
    
    
    few minor corrections
    
    Just throw EncodingError, don't put the diagnosis in the type: I don'tnthink anyone will try to catch specific types of encoding errorsnanyway (and it'll save me creating more exception types).nAlso, the tag is called "end of content", not "end of input".