---
layout: post
title: "Radical Refactoring: Have the compiler to (some of) the reviewing"
date: 2014-10-18 09:35:32
categories: blog
---
One of the most common sources of bugs is ambiguity: some too-subtle API change that’s missed in a library update and introduces a subtle bug, that finally only gets found out in the field. My answer to that problem is radical: make changes breaking changes — make sure the code just won’t compile unless fixed: the compiler is generally better at finding things you missed than you are.  
  
I recently had to review a chunk of code that ported an application from one platform to a different flavor of that platform. The different flavor in question didn’t support a given library, but because all flavors were compiled from the same source tree, the headers of the unsupported library were still available. Regrettably the only way to distinguish between one flavor of the platform and another at compile-time was using an `#ifdef`.

The code was therefore littered with `#ifdef`s, but the `#include` directive that included the library’s header files was still there — so all the API calls that were no longer supported would still compile (and, in this case, link as well, but do the wrong thing at run-time in oh-so-subtle ways).

In stead of going through all the calls one by one, I asked the developer to surround the `#include` with an `#ifdef` and let the compiler check that none of them had been forgotten. In this case, none of them had.

The compiler didn’t find any sites that had been missed, but had there been any, it would have.

Of course, a better approach would have been to refactor the code so all those `#ifdef`s would no longer have been necessary. That is what had originally been pla ed, but sometimes the economic realities off our work catch up to the cleanliness of our code: sometimes refactoring and doing it right _right now_ is simple too expensive. The question then becomes whether the investment into refactoring will return a real added value to the program — and the answer in this case was “no”.

n