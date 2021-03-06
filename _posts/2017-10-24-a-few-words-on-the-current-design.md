---
title: A few words on the current design 
date: "2017-10-24 12:26 -0400"
comments: true
categories: rubicon
---
If you've been following what's going on in the "visitors" topic branch (you probably haven't) you may be wondering what I'm doing. Fear not: there is method to the madness. 

ASN.1 is all about encoding values and describing types that define the structure of those values. The schema language is defined by a grammar which allows a type to reference types and values by name, but does not impose an order of declaration for those names - i.e. you can reference a name that is defined further along in your schema. This means that when, for example, an enumeration type references a value by its name but that name is not defined yet, that is not necessarily an error. *That*, in turn, means that we can't parse the entire schema in a single pass.

A large part of parsing is about extracting relevant information out of whatever input you're parsing and representing that input in a usable way. The parser generated from the grammar (first defined [here](https://github.com/blytkerchan/-rubicon/commit/80947e580ff7bbb25ef57f73c87bd9948827aab6) and slightly updated, simplified and fixed since) parses the text into a tree of nodes that we can walk through. That representation is very close to the grammar itself but isn't very easy to work with otherwise to generate the code we need to parse the binary version of the values. In order to do that, we need a representation that is closer to the semantic meaning of the types and values being encoded. 

To this end, I have created a fairly simple, and fairly flat, hierarchy of class types, rooted in the `TypeDescriptor` class. The `TypeDescriptor` class represents a single type described and defined in an ASN.1 schema. The classes derived from this class will ultimately be expected to be able to generate the code necessary to serialise, deserialise, and generally work with instances of those types. Serialization will use the `DEREncoder` whereas deserialization will use the `DERDecoder`. 

The compiler, as it goes through the parse tree, constructs a second tree (or rather: a small forest) which encapsulates the syntax encoded in the schema in terms of type descriptors and values. Once that forest is constructed, it will be re-visited a number of times: once to resolve all the internal references and at least once more to generate the code. 

Right now quite a few annotations of this little "forest" are missing: the types currently don't know where they're from, identifiers aren't registered so I can look them up in the second pass, etc. Once I've created the preliminary value types to parse that part of the tree, that annotation will be next.
