---
layout: post
title: "What happens if structures aren’t well-designed"
date: 2012-12-05 18:17:10
categories: blog
---
In my [previous post](http://rlc.vlinder.ca/blog/2012/12/how-to-design-a-struct-for-storage-or-networking/ "How to design a struct for storage or networking"), I explained how to design a structure for persisting and communicating. I didn’t say why I explained it — just that things get frustrating if these simple rules aren’t followed. In this post, I will tell you why I wrote the previous one.  
  
Two or three years ago, I was working on a project that, among several other things, used existing software to communicate between the device I was programming for and another device. The device I was programming for used a binary configuration mechanism that persisted the configuration in binary form directly on disk, in a somewhat structured format. While the structures, as persisted, did include a header that told the reader how much to skip to get to the next section, and a magic number (or rather: a GUID) for each section. The structures in question were managed by a tool with a graphical interface and the generated configuration was included in the firmware with the software I was writing. My software was simply to open the file, get a chunk out of it and pass that chunk to the library doing the communicating, so it would know how to co ect and what its parameters were to be.

This worked just fine for a very long time, but having moved on to other projects and the software in question not needing any maintenance until very recently, the library code being used for the communications had been allowed to evolve without “my” software being updated with it. I put “my” in quotes here because the software in question is proprietary software that I do not own — I just wrote it. The risk associated with not maintaining the software concurrently with the communications software was known, understood, and managed so there was no real objection to going down this path.

About three weeks ago, I was asked to help with a massive update of the project’s basic software: the OS, all of the libraries and several other chunks of software I didn’t write had all evolved while the software I had written had been left standing still. Now, a different device to communicate with had to be supported, some-one had been working on that for a few months already[1](http://rlc.vlinder.ca/blog/2012/12/what-happens-if-structures-arent-well-designed/#footnote_0_1979 "I knew about that: I’d helped him a few times already") and a delivery date was nearing, but the update of the bulk of the firmware was in trouble: the system didn’t communicate.

There were two problems that had to be solved: the first was in the OS, the second was in the application-level software.

In the OS, the boot communicated the IP addresses and similar information to the main OS through a mailbox structure in memory. That mailbox structure had been changed independently in two branches. Both had added the same field, `timestamp` to the information to be communicated. In one branch, another field had been shortened from 16 to 12 bytes and the `timestamp` had been inserted. In the other branch, the `timestamp` had been added to the end of the structure.

This is a classic example of why 

  1. you should reserve fields for future use; and
  2. you should consistently add new fields to the end of a structure if no reserved fields are available.

Not following these two simple rules meant I now had to detect which boot was ru ing to know which format of the mailbox was being used, and translate from one format to the other — in a way that was transparent to the system — if I found an incompatible boot.

Once the OS was fixed and tested, we checked that this fixed the symptoms of the problem as well, which is when we found the second problem — the system still wasn’t communicating (though we could now ping and telnet into it, which was definite progress). The communications library failed to initialize.

Tracing through the initialization routine the problem was found easily enough: the chunks of data containing the configuration contained invalid values. We couldn’t verify whether the data being read was in any way misaligned or otherwise corrupted because _almost none_ of the rules I set out in my previous post had been followed: 

  * there were no magic numbers
  * the only version information included applied to the whole group — none for individual chunks
  * the structures contained invisible holes, meaning we had to mentally add padding

Due to this lack of following design principles, I only found out the next morning that another one of my design rules had also not been followed: a structure had been inserted in the sequence somewhere in the middle. Because some of the code I was ru ing was “unaware” of this, the data being read was offset by several hundreds of bytes — something that would easily have been noticed if we had had magic numbers to look for. When I did finally find the problem, the fix took a few minutes. Several hours were lost searching for a cause in several wrong places, however.

Hence, two blog posts…

  1. I knew about that: I’d helped him a few times already