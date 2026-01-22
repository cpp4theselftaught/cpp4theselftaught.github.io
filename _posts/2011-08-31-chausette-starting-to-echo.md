---
layout: post
title: "Chausette: Starting to echo"
date: 2011-08-31 20:43:27
categories: blog
---
n n n n n n n  n  n  The last time we looked at the code for Chausette, before we went on a tangent about functional programming, we were working on a bit of example code that could accept a TCP co ection and output to the console whatever it received. That was [episode 28: “Event-driven software, step 1: select”](http://rlc.vlinder.ca/blog/2010/12/event-driven-software-step-1-select/ "Event-driven software, step 1: select"). This time, we will build onto that code and start by sending data back over the co ection.  
  
We will go through three steps in this episode: 

  1. adding anonymous (but named) attributes to the `Socket` class
  2. echoing incoming data, using a `vector` as the buffer; and
  3. echoing more data than the socket can handle in a single write

## 1- Adding anonymous (but named) attributes to the `Socket` class

We will want to be able to associate data — the data we’ve received — with the socket we’ve received it on, _as_ the data we want to send. To do that, we will create an `Attributes` class which will allow for a simple integer-to-attribute mapping, in which the attribute can have any type — modeled after the attributes you can associate with I/O streams.

In fact, the standard library’s I/O streams contain three functions of interest: `xalloc`, `iword` and `pword`. These three functions allow you to allocate an integer (using `xalloc`) for later use as a key to an anonymous attribute of any stream. The other two functions allow for access to that attribute as an integer or as a pointer.

These attributes are very useful in all kinds of situations, but they are not type-safe. Our implementation will be.

Let’s first have a look at our new base class – which is where all the magic will happen:

```cpp #ifndef vlinder_chausette_core_attributes_h #define vlinder_chausette_core_attributes_h #include "Details/prologue.h" #include  amespace Vlinder { amespace Chausette { amespace Core { class VLINDER_CHAUSETTE_CORE_API Attributesn { public : static unsigned int alloc(); n boost::any& get(unsigned int index); const boost::any& get(unsigned int index) const; n private : static const unsigned int id_max__ = 48; n boost::any attributes_[id_max__]; static unsigned int next_id__; }; }}} #endif ``` 

This class, which is part of [our first commit for this installment](https://gitorious.org/chausette/chausette/commit/c218d63aa002c1a772ab810c62beed003c8562be "the commit on Gitorious"), contains an array of `boost::any` instances to hold our attributes. The `boost::any` class is a type-safe single-entry container. More exactly, it is a type-safe variant type without implicit conversion that can contain any (static) type variable and is based on and article called “Valued Conversions” by Kevlin He ey which appeared in C++ Report in 2000[1](http://rlc.vlinder.ca/blog/2011/08/chausette-starting-to-echo/#footnote_0_1650 "“Valued Conversions” by Kevlin He

ey, C++ Report 12\(7\), July/August 2000\)"). We will use it to provide type-safe anonymous attributes to the `Socket` class.

In order to do that, `Socket` will _privately_ derive from `Attributes`:

```cpp struct Socket : private Vlinder::Chausette::Core::Attributes { Socket(int fd, int parent_fd = -1) : fd_(fd) , parent_fd_(parent_fd) , read_avail_(false) , write_avail_(false) , exc_avail_(false) { /* no-op */ } n using Vlinder::Chausette::Core::Attributes::alloc; using Vlinder::Chausette::Core::Attributes::get; n int fd_; int parent_fd_; bool read_avail_; bool write_avail_; bool exc_avail_; }; ``` 

The reason why it derives _privately_ is because, while we want it to inherit the features provided by the `Attributes` class, we don’t want the relationship between the two classes to be modeled as an _is-a_ relationship — we don’t want to say “a socket is a container of attributes”.

Making the inheritance private prevents the user of our `Socket` class to automatically cast an instance of `Socket` to an instance of `Attributes` and prevents `static_cast` and `dynamic_cast` from converting between the two. It also makes the inherited accessors private, but they are made public again with the two `using` statements

Using these attributes, we can associate a buffer of data to send with the socket. Doing that, we can add data to be sent to the socket at any time, and send it as soon as data is ready to be written to the socket.

## 2- Echoing incoming data, using a `vector` as the buffer

Let’s see what that looks like.

First, we need to get an attribute ID from the `Attributes` class, allocating it for future use. We only need one of those for the whole program per kind of data we want to associate with the socket, but we shouldn’t assume that we will always be the first (and only) piece of code to want to associate something with a socket. We can assume, however, that there will only be one instance of the `Applicatio ` class, so we can handle the association in the constructor of that class.

```cpp Applicatio ::Applicatio () : server_(0) , socket_attribute_id_(Socket::alloc()) { WSADATA wsadata; WSAStartup(MAKEWORD(2, 2), &wsadata;); } ``` 

The allocation is on line 3.

Now, in our particular case, we want to associate the data we receive with the socket, because that is the data we will be sending. We do that by getting the attribute, seeing if there’s anything there and associating an empty buffer with the socket if there isn’t, like so:

```cpp if (socket.get(socket_attribute_id_).empty()) { socket.get(socket_attribute_id_) = vector< char >(1024); } else { /* already have a buffer */ } ``` 

Note that on line 3 of this snippet, we initialize the vector to have a size of 1 KiB — 1024 bytes. That’s because we will use this buffer as a receive buffer as well as as a send buffer, and in the code immediately following, we will use it as such:

```cpp vector< char > &buffer; = any_cast< vector< char >& >(socket.get(socket_attribute_id_)); buffer.resize(buffer.capacity()); unsigned int data_read(buffer.size()); server_->read(socket, &buffer;[0], &data;_read); ``` 

Note that in line 7, we get a _reference_ to the vector so any changes we make the the vector are made directly to the attribute and we don’t need to make any copies. On line 8, we resize the buffer to its full capacity (meaning that if at any point we made it larger than the one KiB we initialized it to, we will have all of that space available) and we then call `read` on the server.

As you can probably tell (or perhaps remember), `read` returns the number of bytes actually read in the parameter we give it, so we now have to resize the buffer back to the size of the data we actually got and, because we want to echo, we will send it back:

```cpp buffer.resize(data_read); server_->write(socket, &buffer;[0], &data;_read); buffer.erase(buffer.begi (), buffer.begi () + data_read); ``` 

Note that on line 13, we erase anything we sent from the buffer – but we don’t actually necessarily think everything was sent — and it is not an error if that was not the case. That’s because the implementation will call our `onWriteReady` method when we can send more data, which looks like this:

```cpp /*virtual */void Applicatio ::onWriteReady(Socket &socket;) { if (socket.get(socket_attribute_id_).empty()) { /* no-op */ } else { vector< char > &buffer; = any_cast< vector< char >& >(socket.get(socket_attribute_id_)); if (buffer.empty()) { /* no-op */ } else { unsigned int data_writte (buffer.size()); server_->write(socket, &buffer;[0], &data;_writte ); buffer.erase(buffer.begi (), buffer.begi () + data_writte ); } } } ``` 

As you can see, this method doesn’t do anything if there’s no buffer associated with the socket, or if the associated buffer is empty. Otherwise, it attempts to send anything it can and erases what it could send from the buffer.

## 3- Echoing more data than the socket can handle in a single write

There’s very little chance of that code ever being called if all we do is echo, however, so we could do a bit more than that – say echo everything four times. That means our `onDataReady` function will now look like this:

```cpp /*virtual */void Applicatio ::onDataReady(Socket &socket;) { if (socket.get(socket_attribute_id_).empty()) { socket.get(socket_attribute_id_) = vector< char >(1024); } else { /* already have a buffer */ } vector< char > &buffer; = any_cast< vector< char >& >(socket.get(socket_attribute_id_)); buffer.resize(buffer.capacity()); unsigned int data_read(buffer.size()); server_->read(socket, &buffer;[0], &data;_read); buffer.resize(data_read * 4); std::copy(buffer.begi (), buffer.begi () + data_read, buffer.begi () + data_read); std::copy(buffer.begi (), buffer.begi () + (data_read * 2), buffer.begi () + (data_read * 2)); server_->write(socket, &buffer;[0], &data;_read); buffer.erase(buffer.begi (), buffer.begi () + data_read); } ``` 

Notice the difference? It’s on lines 13, 14 and 15, where we resize the buffer to four times the amount of data we received and copy the data into the expanded part of the buffer.

Now, there’s a subtle – but present — bug in this code (and unlike the one I can’t seem to find anymore in the `Yard` class from a few months back, I’ll tell you where it is.

Imagine you’re sending and receiving data more or less at the same time. Look at what happens on lines 10, 11 and 12 of `onDataReady` and try to figure out what the bug is — and how to fix it.

To see the _answer_ click here.To hide the _answer_ click here.

What will happen is that the buffer will be overwritten with whatever you happen to receive, meaning some of the data you were supposed to echo will not be echoed. One way to fix that is to use a separate buffer for receiving. Another way to fix that is to automatically append to the buffer you’re receiving in by initially resizing the buffer to – e.g. – 1 KiB beyond the data that’s already in there. The latter solution is slightly less costly w.r.t run-time (but may ultimately be more costly in space overhead) and looks like this:

```cpp /*virtual */void Applicatio ::onDataReady(Socket &socket;) { bool needed_to_initialize(false); std::vector< char >::size_type offset(0); if (socket.get(socket_attribute_id_).empty()) { socket.get(socket_attribute_id_) = vector< char >(1024); needed_to_initialize = true; } else { /* already have a buffer */ } vector< char > &buffer; = any_cast< vector< char >& >(socket.get(socket_attribute_id_)); if (! eeded_to_initialize && buffer.empty()) { buffer.resize(buffer.capacity()); } else if (! eeded_to_initialize) { offset = buffer.size(); buffer.resize(offset + 1024); } else { /* needed to initialize - so no need to account for data already in the buffer */ } unsigned int data_read(buffer.size() - offset); char *read_ptr(&buffer;[0]); read_ptr += offset; server_->read(socket, read_ptr, &data;_read); buffer.resize(offset + (data_read * 4)); std::copy(buffer.begi () + offset, buffer.begi () + offset + data_read, buffer.begi () + offset + data_read); std::copy(buffer.begi () + offset, buffer.begi () + offset + (data_read * 2), buffer.begi () + offset + (data_read * 2)); unsigned int data_writte (buffer.size()); server_->write(socket, &buffer;[0], &data;_writte ); buffer.erase(buffer.begi (), buffer.begi () + data_writte ); } ``` 

  1. [“Valued Conversions” by Kevlin He ey, C++ Report 12(7), July/August 2000)](http://www.two-sdg.demon.co.uk/curbralan/papers/ValuedConversions.pdf "The PDF")