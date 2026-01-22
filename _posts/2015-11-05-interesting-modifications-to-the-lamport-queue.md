---
layout: post
title: "Interesting modifications to the Lamport queue"
date: 2015-11-05 20:28:03
categories: blog
---
While researching lock-free queue algorithms, I came across a few articles that made some interesting modifications to the Lamport queue. One made it more efficient by exploiting C11’s new memory model, while another made it more efficient by using cache locality. As I found the first one to be more interesting, and the refinements more useful for general multi-threaded programming, I thought I’d explain that one in a bit more detail.  
  

**The TL;DR:** I

  * provide a brief explanation of lock-free queue categories
  * explain an article by Nhat Minh Le _et al._ in programmer-ese
  * provide their improvement upon the Lamport queue, [with code](https://github.com/blytkerchan/Lamport)
  * show why alternative approaches don’t work
  * explain what a data race is, and how the C11 memory model fits in and addresses it

  
The article I will explain part is “Correct and Efficient Bounded FIFO Queues” by Nhat Minh Le _et al._ , which you can find [here](http://dx.doi.org/10.1109/SBAC-PAD.2013.8). I have set up a [Git repository on GitHub](https://github.com/blytkerchan/Lamport) with the C11 code. In order to build it, you need at least GCC version 4.9. In order to test it properly, you need something like Thread Sanitizer, which is included in GCC and used by the provided Makefile — but the article itself contains ample proof that the code will work.

Let’s first take a look at the Lamport queue, as originally presented by Lamport in “Proving the Correctness of Multiprocess Programs” (available [here](http://dx.doi.org/10.1109/TSE.1977.229904)) as an example of a lock-free queue. It wasn’t ostensibly designed to be particularly efficient but rather as a nice, simple, easy-to-analyse example of a multi-process program[1](http://rlc.vlinder.ca/blog/2015/11/interesting-modifications-to-the-lamport-queue/#footnote_0_3679 "This is another reason why I prefer the article I’m explaining rather than the other candidate which caught my attention: the tone is much friendlier").

The code for Lamport’s queue, translated to C11, looks like this:

```c struct LamportQueue { atomic_size_t front_; atomic_size_t back_; T data_[SIZE]; }; ``` 

This defines the structure of the queue itself. The queue is a lock-free single-producer/single-consumer (SPSC) single-in/single-out (SISO) FIFO queue.  
This is where you say “What does that mean?”.

Queues are classified along various categories, according to the guarantees they give you. Among various others (some of which I will discuss below), there is the question of “how many threads can push something into the queue at the same time?”, rephrased as _single-producer_ , or _multi-producer_ because generally, if you can push with two threads at the same time, you can push with three threads at the same time, etc.[2](http://rlc.vlinder.ca/blog/2015/11/interesting-modifications-to-the-lamport-queue/#footnote_1_3679 "Note that this is not always the case!").

Analogously, you can ask “with how many threads can I pop stuff from the queue at the same time?”, rephrased as _single-consumer_ or _multi-consumer_. With these two questions answered, we now have four classes of queue algorithms: SPSC, MPSC, SPMC and MPMC. If you go out looking for queue algorithms, you’ll find the SPSC kind is the most ubiquitous.

A second set of questions you can ask is “how many values can I push into the queue at the same time?”, rephrased as _single-i_ vs. _multi-i_ — and conversely “how many values can I pop from the queue at the same time?”, rephrased as _single-out_ or _multi-out_. Most queues (lock-free or not) are SISO, but there are also SIMO, MISO and MIMO queues.

A third question is about the _order_ of the things that go in vs. the things that go out. Basically, there are three orders: _first-in-first-out (FIFO)_ , _last-in-first-out (LIFO — also sometimes called first-in-last-out or FILO, this is basically a stack)_ and _undetermined_ which basically means you don’t know but in which case there’s generally a note saying something like “FIFO in the general case” indicating that, while we can’t guarantee a specific order, it will generally look like this…

Now, I almost glossed over the “lock-free” part. [Gotsman _et al._](http://dx.doi.org/10.1145/1480881.1480886) provide a nice classification of non-blocking algorithms:

Wait-freedom:
    Every ru ing thread is guaranteed to complete its operation, regardless of the execution speeds of the other threads. Wait-freedom ensures the absence of livelock and starvation.
Lock-freedom:
    From any point in a program’s execution, some thread is guaranteed to complete its operation. Lock-freedom ensures the absence of livelock, but not starvation.
Obstruction-freedom
    Every thread is guaranteed to complete its operation provided it eventually executes in isolation. In other words, if at some point in a program’s execution we suspend all threads except one, then this thread’s operation will terminate.

Wait-freedom is the Holy Grail of non-blocking algorithms: if you can find a non-trivial wait-free algorithm that suits a general need, you will have earned the respect of many a programmer. Lamport’s algorithm is actually wait-free, but it has the caveat of failing when the queue is full/empty (which is OK in many cases, but in some cases, it means the producer has to loop back and wait for there to be space available, so the algorithm really becomes lock-free rather than wait-free)[3](http://rlc.vlinder.ca/blog/2015/11/interesting-modifications-to-the-lamport-queue/#footnote_2_3679 "So close, yet so far away….").

Let’s get back to the code. Initializing the structure is straight-forward:

```c void LamportQueue_init(struct LamportQueue *queue) { atomic_init(&queue-;>front_, 0); atomic_init(&queue-;>back_, 0); } ``` 

Pushing into the queue is interesting: as Nhat Minh Le _et al._ describe it, each end (the pushing and pulling end) can consider one of the two indices as _ow_ and the other as _foreig_. A process has the right to read and modify its own index, but can only read the foreign one — no modification allowed there. Keeping that in mind, you just have to decide which end you push onto (we’ll take the tail) and which end you pop off of (the head). Hence, within `push` the tail, or `back_` is owned while the head, or `front_` is foreign, and vice-versa for pop.

So, pushing is a matter of getting the location to store the data to (line 28), checking whether it is available (lines 29 through 35), putting the data there (line 36), and publishing the fact that the data is there by incrementing the appropriate index (line 37).

```c bool LamportQueue_push(struct LamportQueue *queue, T elem) { size_t b, f; b = atomic_load_explicit(&queue-;>back_, memory_order_seq_cst); f = atomic_load_explicit(&queue-;>front_, memory_order_seq_cst); if ((b + 1) % SIZE == f) { retur false; } else { /* not full */ } queue->data_[b] = elem; atomic_store_explicit(&queue-;>back_, (b + 1) % SIZE, memory_order_seq_cst); retur true; } ``` 

Popping is, of course, similar to pushing: read the place where the data should be (line 44), check whether the queue isn’t empty (lines 45 through 51) read the data (line 52) and publish the fact that it’s been read by incrementing the owned index (line 53).

```c bool LamportQueue_pop(struct LamportQueue *queue, T *elem) { size_t b, f; f = atomic_load_explicit(&queue-;>front_, memory_order_seq_cst); b = atomic_load_explicit(&queue-;>back_, memory_order_seq_cst); if (b == f) { retur false; } else { /* not empty */ } *elem = queue->data_[f]; atomic_store_explicit(&queue-;>front_, (f + 1) % SIZE, memory_order_seq_cst); retur true; } ``` 

Lock-freedom is nice, but you want to avoid _contentio_ which is something lock-freedom alone will not do. On modern systems, contention can happen in all kinds of hidden places: loading a shared variable’s value, for example, may require the compiler or processor to emit _memory barriers_ to ensure the value you see is the value you really want to see (or the value the compiler/processor thinks you really want to see). That might mean having to synchronize with other CPUs or other CPU cores, interrupting the normal workflow of some or all of them; going all the way through to memory, slowing you — and possibly others — down along the way.

So, how do you get rid of such contention? One way exemplified by Nhat Minh Le _et al._ is to get rid of memory barriers. The approach they take in the article is well-thought-out, but frankly a bit boring — so I thought I’d mix things up a little and just make everything “relaxed” (changing `memory_order_seq_cst` to `memory_order_relaxed` throughout the code) to show that that doesn’t work.

Ru ing what I’ll call the “hippie” version, compiled with ThreadSanitizer, you get this warning:

``` ==================nWARNING: ThreadSanitizer: data race (pid=7546) Read of size 4 at 0x7ffc720b0b10 by thread T2:n #0 LamportQueue_pop /home/rlc/lamport/lamport.c:50 (lamport+0x000000000e33) #1 consumer /home/rlc/lamport/lamport.c:73 (lamport+0x000000000f4b) #2 (libtsan.so.0+0x000000023629) n Previous write of size 4 at 0x7ffc720b0b10 by thread T1:n [failed to restore the stack] Location is stack of main thread. Thread T2 (tid=7549, ru ing) created by main thread at:n #0 pthread_create (libtsan.so.0+0x0000000274f7) #1 main /home/rlc/lamport/lamport.c:89 (lamport+0x000000001015) n Thread T1 (tid=7548, ru ing) created by main thread at:n #0 pthread_create (libtsan.so.0+0x0000000274f7) #1 main /home/rlc/lamport/lamport.c:88 (lamport+0x000000000fec) nSUMMARY: ThreadSanitizer: data race /home/rlc/lamport/lamport.c:50 LamportQueue_popn==================nThreadSanitizer: reported 1 warnings ``` 

This basically means that there’s no way of knowing which version of `back_` the consumer is reading, w.r.t. the associated data: because of the relaxed memory ordering, the the reads and writes in the producer thread aren’t necessarily visible in the same order in the consumer thread, and vice-versa.

This warrants a bit more explanation.

When you write your code, you might expect the compiler to translate your code into the equivalent instructions in assembly language, which are then translated into opcodes, one by one, which are then faithfully executed, in order, by the computer. However, if that is really what you believe is going on, many a computer scientist or software engineer will ask you what century you think we’re in. In this century, the hardware really only pretends to do something similar to what the software tells it to do, and at the moment it sees the software, it really is only a facsimile of what the programmer originally wrote. In order for the computer to do what you want it to do efficiently, we have to give it an enormous amount of latitude as to what exactly it does, and in what order.

This is where the C11 memory model comes in: while, in the spirit of the rest of the C language, most of it is undefined, it defines the order of things in terms of _happens-before_ and related notions. Happens-before is the most important of these in that it addresses the notion of a _race conditio_ or _data race_ : a data race occurs when a process tries to read a value ![hat{x}](http://s0.wp.com/latex.php?latex=%5Chat%7Bx%7D&bg=ffffff&%23038;fg=000000&%23038;s=0) ftom a variable ![x](http://s0.wp.com/latex.php?latex=x&bg=ffffff&%23038;fg=000000&%23038;s=0) but it is undefined whether the write that produces that value has occured yet, or is perhaps even still in progress; or when a process tries to write to ![x](http://s0.wp.com/latex.php?latex=x&bg=ffffff&%23038;fg=000000&%23038;s=0) while another process also tries to write to ![x](http://s0.wp.com/latex.php?latex=x&bg=ffffff&%23038;fg=000000&%23038;s=0). If ![x](http://s0.wp.com/latex.php?latex=x&bg=ffffff&%23038;fg=000000&%23038;s=0) is not shared, this ca ot happen but if it is, _reads and writes to shared variables may appear out-of-sequence to other processes/threads_.

This gets us back to what I said earlier: between the code you write and what the computer executes, there may be a world of difference. The “hippie” version of the code above, with its relaxed reads and writes on atomic shared variables only guarantees that no thread/process will see any intermediate values — values that are neither the previous nor the new value — but it does not guarantee anything of the sort for non-atomic shared variables (such as `data_`) nor does it say anything about the ordering between writes to `data_` and writes to `back_`, as visible from the consumer, nor reads from `data_` and writes to `front_` as visible from the producer.

Of course, this does not mean that all reads and writes have to use `memory_order_seq_cst`: `memory_order_seq_cst` emits a _memory barrier_ that makes anything that was sequenced-before it visible before it — which is usually overkill. To know what kind of `memory_order_*` you need, you need to ask yourself: what reads/writes may become visible after this point? and who else (what other thread/process) can see this shared state?

With this in mind, let’s take another look at `LamportQueue_pop`:

```c bool LamportQueue_pop(struct LamportQueue *queue, T *elem) { size_t b, f; f = atomic_load_explicit(&queue-;>front_, memory_order_seq_cst); b = atomic_load_explicit(&queue-;>back_, memory_order_seq_cst); if (b == f) { retur false; } else { /* not empty */ } *elem = queue->data_[f]; atomic_store_explicit(&queue-;>front_, (f + 1) % SIZE, memory_order_seq_cst); retur true; } ``` 

On line 44, we load our _ow_ member variable, `front_`. We (the context of the thread the code is ru ing in) are the only ones to ever write to this variable, so we know that the only sequencing that can happen — the only order in which we can see changes to this member — is the order we impose on it ourselves. This means we can breathe easily: there is no way for someone else (another thread) to mess up what we see when we look at this variable — we can _relax_.

More formally, reads from shared variables the reading thread only writes to itself can be relaxed because we only need sequenced-before ordering.

On line 45, we read from a _foreig_ variable, so we will need some kind of barrier to make sure that any reads of our shared state — any reads of the data in our queue — ca ot be ordered before this read. In the same vein, on line 53 we write to our _ow_ variable with the full knowledge that another thread will read it as a _foreig_ variable, so we need to make sure no stores we do on the shared state are ordered after that write. I.e., we ca ot be seen to read from the shared state before reading the foreign variable and thus _acquiring_ the shared state, and we ca ot be seen to write to the shared state after writing to our own variable to _release_ the shared state.

The wording is important here: unless we tell it otherwise, the compiler/CPU is allowed to re-order anything we do in a single thread as long as from the thread itself, everything still _seems_ to have occurred in the same order. The _visible order_ from any other thread may well be different. Memory barriers and atomic operations affect the way things are seen from outside the thread. So when I say that the thread “ca ot be seen to read from the shared state before reading the foreign variable” that means that the visible order of those operations, as seen from outside the thread, should be such that the read from the foreign atomic variable _happens-before_ the read from the shared data.  
  
[_Continued…_](http://rlc.vlinder.ca/blog/2015/11/interesting-modifications-to-the-lamport-queue-part-ii/)

  1. This is another reason why I prefer the article I’m explaining rather than the other candidate which caught my attention: the tone is much friendlier
  2. Note that this is not always the case!
  3. So close, yet so far away….