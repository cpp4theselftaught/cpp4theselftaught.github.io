---
layout: post
title: "How to design a struct for storage or communicating"
date: 2012-12-04 22:21:06
categories: blog
---
One of the most common ways of “persisting” or communicating data in an embedded device is to just dump it into persistent storage or onto the wire: rather than generating XML, JSON or some other format which would later have to be parsed and which takes a lot of resources both ways, both in terms of CPU time to generate and parse and in terms of storage overhead, dumping binary data into storage or onto the wire has only the — inevitable — overhead of accessing storage/the wire itself. There are, however, several caveats to this, some of which I run into on a more-or-less regular basis when trying to decipher some of that data, so in stead of just being frustrated with hard-to-decipher data, I choose to describe how it should be done in stead.

Note that I am by no means advocating anything more than a few simple rules to follow when dumping data. Particularly, I am _ot_ going to advocate using XML, JSON or any other intermediary form: each of those has their place, but they neither should be considered to solve the problems faced when trying to access binary data, nor can they replace binary data.

## Necessary parts

There are two things that any structure that is communicated[1](http://rlc.vlinder.ca/blog/2012/12/how-to-design-a-struct-for-storage-or-networking/#footnote_0_1966 "and I include writing to persistent storage and reading it back later in “communication” because that’s what it is: the software reading the data may very well be different from the software writing it — be it different versions of the same software, or different software altogether") in binary form should have:

  1. a **magic number** , preferably one that is at exactly four bytes in length and one that is chosen to be human-readable, either when displayed as HEX or when displayed as “deciphered” ASCII  
Good examples are `0xdeadbeef`; `0x _N_ badf00d` in which _N_ is replaced by a hexadecimal value that might mean something — you have 16 options, and you can put the N at the end, so you really now have 32 options!!; `'CODE'` (or `0x434f4445` in this case) in which CODE is replaced by something descriptive for the structure’s content. For example, if it contains a config for a potato peeler, `'PCFG'` (or `0x50434647`) would do just fine. The idea is to have some magic number that’s easy to recognize when displayed by a memory debugger or when dumped by a run-of-the-mill binary editor/viewer.
  2. the **versio** of the structure. This can be a simple incremental counter — it can even be part of the magic number of you don’t want to “waste” bytes, but it really should be in there. Ideally, it should consist of at least two parts: “current” and “age”, the idea being that you increment both “current” and “age” if you add something, and that you increment “current” and set “age” to 0 if you remove something or change the meaning of some part in a way no longer compatible with previous versions. That way, any-one who reads the structure can very easily see if they can _understand_ the structure:n ```c if (data.magic_ == POTATO_PEELER_CONFIG_MAGIC) { if ((data.version_.current_ - data.version_.age_) == (POTATO_PEELER_CONFIG_CURRENT - POTATO_PEELER_CONFIG_AGE)) { if (data.version_.current_ >= POTATO_PEELER_CONFIG_CURRENT) { // current or newer version - read it as if // it's current. // We should be able to ignore anything // added since (because the implementor // declared us to be forward-compatible, // after all) } else { // older version. Assume default values for // newer fields, or follow some kind of logic // to keep compatibility -- after all, the // implementor did declare us to be // backward-compatible } } else { /* incompatible version - maybe fall back on conversion code..? */ } } else { /* not something we understand - wrong magic number */ } ``` 

With just these two in place on every persisted structure, I would have saved hours of futile staring at memory dumps and binary dumps of files from legacy (and current) systems that I was asked to debug. Basically, every persisted structure should begin like this:

```c struct PotatoPeelerConfiguration_struct { uint32_t magic_; uint32_t version_; ``` 

or, if we want the code above to compile[2](http://rlc.vlinder.ca/blog/2012/12/how-to-design-a-struct-for-storage-or-networking/#footnote_1_1966 "There is some religious debate over whether or not to do typedef struct Version_struct Version; in C headers, so I left that out, though I usually would have included it for convenience."):

```c struct Version_struct { uint16_t current_; uint16_t age_; }; struct PotatoPeelerConfiguration_struct { uint32_t magic_; struct Version_struct version_; ``` 

## The structure’s structure

What’s wrong with this picture:

```c struct Blah { uint32_t ulThingy; uint8_t ucThingy; uint16_t usThingy; }; ``` 

Hint: it’s not the Hungarian notation!

There’s an invisible hole in this structure[3](http://rlc.vlinder.ca/blog/2012/12/how-to-design-a-struct-for-storage-or-networking/#footnote_2_1966 "At least, there is on the vast majority of platforms"). Between `ucThingy` and `usThingy` there is a one-byte hole due to the structure’s members’ alignment.

The vast majority of compilers will insert a hole into the structure to make sure the `usThingy` member is aligned on a “natural” two-byte boundary. _That is the right thing to do_ , because many hardware platforms will be _very_ picky on mis-aligned data. ARM, for example, will throw a ‘data abort’ at you whereas x86 will simply slow down to a crawl.

**Please don’t make the mistake of using`#pragma pack` for this**: use `#pragma pack` only if you _know_ it has no effect, and then only if you have a whole bunch of `assert`ions in your unit tests, which are run every night, checking that the `#pragma pack` has no effect on any of the platforms you target[4](http://rlc.vlinder.ca/blog/2012/12/how-to-design-a-struct-for-storage-or-networking/#footnote_3_1966 "In other words: just don’t use it — it’s useless."). Using `#pragma pack` otherwise can cause mis-alignment of the contents of the structure which on some platforms (like ARM) can cause crashes.

_Do_ use filler variables to fill the holes, like this:

```c struct Blah { uint32_t magic; uint32_t versio ; uint32_t ulThingy; uint8_t ucThingy; uint8_t reserved; uint16_t usThingy; }; ``` 

Note the magic number and version as well, which should _of course_ be at the start of the structure.

If you’re saving a whole bunch of data to a file, or sending it over a wire, please structure it so we can skip the parts we don’t care about – e.g. by including a header with a `size` field for a section of data objects that we might want to skip over. Every object in the section should still have its own magic number and version, of course, but at least we’ll know that the next 148 bytes are configuration for orange peelers (we’re interested in potato peelers, so we’ll skip those 148 bytes, thank you very much).

If you add something to a structure, _unless you have reserved some space in the structure for that purpose_ add it to the end: you are least likely to create compatibility problems that way.

If you’re adding to a collection of objects (as described above) the same applies: make it a complete structure (magic, version and all) and add it to the end.

If you’re designing a structure that is going to be part of a collection of structures communicated somewhere, make sure its size is a multiple of the largest primitive normally used — e.g. a multiple of eight bytes, or four bytes if you don’t go larger than 32-bit integers. This allows the structures, once read into appropriately-aligned memory, to be automatically appropriately aligned when accessed in that appropriately-aligned memory. Because most functions that dump data to the medium don’t pad structures (as the compiler does when you create an array of objects that don’t follow this rule) you won’t be able to count on alignment otherwise.

## Other bits[5](http://rlc.vlinder.ca/blog/2012/12/how-to-design-a-struct-for-storage-or-networking/#footnote_4_1966 "I was going to call this section “Optional bits” but it’s not really optional any more than the text itself implies — I don’t want you to skip over this section just because I said it was optional")

If the data you are dumping is somehow variable-sized (i.e. it’s the header of something), _please include the size_ so we know how much data to skip. If need be the size can be used in _lieu_ of a version (as one Redmond-based company often does).

You may want to include a few reserved fields for future use. _Do_ expect them to be 0 by default, or include some kind of flag when set to 0 if the 0 means something, and _please do_ `memset` structures to 0 before filling them in because you _will_ forget some of the fields some of the time, and you don’t want random values to end up in there.

Don’t use already-common magic numbers, such as `0xfeeefeee` or `0xcccccccc` etc. While they’re easy to recognize and perfectly fine as magic numbers in their own right, encountering them usually means **bug** and really stands out to they hardened debugger’s eye.

If your structure contains strings, try to zero-terminate them if at all possible. Many, many programmers forget to check for zero-termination when they output something from the struct, which causes many, many crashes or other random behaviors.

## Reading and writing

Writing is the easy part, so let’s start with that.

If you have a structure in memory, writing it somewhere is simply a case of calling the appropriate `write()` function passing it a pointer to your structure and the size, like this: ``` retval = write(&data;, sizeof(data)); ``` 

You don’t have to worry too much about issues such as alignment, because the write function will ready the thing byte by byte if need be.

Reading it into memory is another matter: while in most cases you still don’t need to worry about alignment, you just might have to if the reading function hands you a pointer rather than the other way around: it may not be aligned properly, so you can’t just cast it to the type you want. In stead, use `memcpy` to copy the data into a temporary variable of the right type, so the compiler can align it properly for you.

Also use the version information you stored to know what the size of the data you received is – it may be different from what you were expecting as the structure may have grown since you wrote your code, or since the code that sent the data was written. Version information will also tell you something about the meaning of the contents of the structure, which may have changed or may need to be set to some default value if it wasn’t provided before.

So, reading data — even binary data — from any kind of storage or communications medium is really _parsing_ : you should carefully design how it’s done and keep in mind that things change over time: some intern may change the code one day having neither read this post nor anything else useful to his job. While there is only so much you can do to protect yourself from that particular intern, you can at least try to be graceful about erroring out when you encounter one of his bugs.

HTH

rlc

  1. and I include writing to persistent storage and reading it back later in “communication” because that’s what it is: the software reading the data may very well be different from the software writing it — be it different versions of the same software, or different software altogether
  2. There is some religious debate over whether or not to do `typedef struct Version_struct Version;` in C headers, so I left that out, though I usually would have included it for convenience.
  3. At least, there is on the vast majority of platforms
  4. In other words: just don’t use it — it’s useless.
  5. I was going to call this section “Optional bits” but it’s not really optional any more than the text itself implies — I don’t want you to skip over this section just because I said it was optional