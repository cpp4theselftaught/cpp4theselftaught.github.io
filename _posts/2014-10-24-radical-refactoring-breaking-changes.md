---
layout: post
title: "Radical Refactoring: Breaking Changes"
date: 2014-10-24 16:36:11
categories: blog
---
One of the most common sources of bugs is ambiguity: some too-subtle API change that’s missed in a library update and introduces a subtle bug, that finally only gets found out in the field. My answer to that problem is radical: make changes breaking changes — make sure the code just won’t compile unless fixed: the compiler is generally better at finding things you missed than you are.  
  
Recently, I found a bug in a smart pointer implementation in Acari, Vlinder Software’s toolbox library used for, among other things, the Arachnida HTTP(s) server/client framework. The bug was subtle, not likely to cause problems in most current deployments of Arachnida, but limiting for one of our customers (so it had to be fixed).

When I started setting up the necessary testing framework, I came to the conclusion that the bug in question was a design flaw, and that not only the code would have to be changed, but the calling code at at least one of the call sites as well. I now had two things to make sure of:

  1. the design had to be reviewed to make sure no other flaws were present
  2. the calling sites that needed to be changed had to be spotted unambiguously, and changed in a way clearly specified

I decided to review the requirements that were at the base of the original design, clarify the requirement that was missed and led to the flaw, set up the necessary test cases for each of the functional requirements, design a new implementation to meet all the requirements, and implement that new design. This decision led to a delay in the release of version 2.3 of Arach ida (which was pla ed for the end of 2014Q3 but will now come out early-to-mid 2014Q4) — which made it an executive decision.

Luckily, I’m the sole proprietor for Vlinder Software as well as its chief analyst — it says so on my business cards — so these type of decisions inevitably come down to me. I looked in the mirror and gave myself the go-ahead (without the mirror bit). I also informed the customer personally that, though his use-case wasn’t supported _at the moment_ , it would be in version 2.3 of the server framework.

I then proceeded to coding the new smart pointer in a new library, according to the new design in a test setup designed specifically for it. This required, among other things, changes to the Relacy Race Detector, which are I made available [on GitHub](https://github.com/VlinderSoftware/relacy "GitHub repository of Relacy fork").

The new smart pointer no longer lives in the `Acari` namespace, but had basically the same API as the previous version did. That means that all the calling sites automatically fail to compile if they use the old version, because the fully-qualified name is no longer the same. The buggy use-case will fail to compile even if you change your `using namespace` directives to include the new namespace, because it will disallow an automatic conversion that was possible in the previous design.

Now, this forced me to revise and review all Vlinder Software code that used the old smart pointer from the Acari library, but as we have automated nightly builds that started failing as soon as I committed the “rip out the pointer class” changes in Acari’s master branch, those sites were easy to find and — because the two APIs are the same for the most part, and the only breaking change is abundantly clear — easy to fix.

Arachnida is now going through the hoops of the release process, with all the (hundreds of) automated test cases ru ing, the security review starting for all modifications made in the months since the previous release, etc. When released, our customers who will upgrade from previous versions of Arachnida to version 2.3 will get a document explaining how to solve the compile-time errors they will probably (almost inevitably) face — a typical upgrade will take no more than 15 minutes to modify the usual call sites where a fully-qualified name for the smart pointer site would be used — and new use-cases will be supported that were not supported before, allowing for more efficient implementations on some devices.

n