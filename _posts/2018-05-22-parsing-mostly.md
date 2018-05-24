---
title: Picking up where we left off
date: "2018-05-22 22:00 -0400"
comments: true
categories: rubicon
---
It's been a while.

I have obviously been quite busy with other things, but I have picked this project up where I left off a few months ago, among other things because I picked up another project in which I need a good ASN.1/DER parser.

I have [committed](https://github.com/blytkerchan/-rubicon/commit/e7a08eeaca254dc2935e22d07e0e6c6406729512) a few fixes and most of the code necessary to parse types and values.

My next stop will be to refactor the code a bit, because the `Listener` class won't just listen -- it will start generating code as well.

The code itself, at least for the last bunch of commits, is actually pretty boring: it's just a matter of being walked through a tree, getting the values out of the tree and putting them in a slightly more interesting object that I can (later) add logic to for code generation and validation, etc. It's basically grunt work, but it has to be done to get a working ASN.1 compiler.

Hopefully, the next parts will be more interesting, and the code will be less obvious (so I'll actually have something that needs to be explained: this blog will become hopelessly boring otherwise).

