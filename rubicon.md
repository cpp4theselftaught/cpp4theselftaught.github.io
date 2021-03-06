---
layout: page
title: Rubicon
date: 2017-08-14 23:03:21 -0400
update: 2017-10-17
---
On July 30, [@jadamcrain](https://twitter.com/jadamcrain) tweeted:

<blockquote class="twitter-tweet" data-lang="en"><p lang="en" dir="ltr">ASN.1 is a terrible DSL for security oriented message definitions. Way too complex. Security message/file formats must be simpler.</p>&mdash; Code Monkey Hate Bug (@jadamcrain) <a href="https://twitter.com/jadamcrain/status/891732011773284352?ref_src=twsrc%5Etfw">July 30, 2017</a></blockquote>
<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

On the surface, he is right, of course: ASN.1 is an overly complex domain-specific language which consists of two major categories of languages: a schema language, specified in X.680, X.681, X.682, and X.683; and a number of encodings. There is, however, one encoding in there that I happen to like for its mix of efficiency and simplicity: it's called DER, for Distinguished Encoding Rules, and is a subset of BER, the Basic Encoding Rules, both of which are defined in X.690 (along with the Canonical Encoding Rules).

DER is a nice encoding in that it consistently encodes values as type-length-value types which the values themselves can be sets or sequences of type-length-value tuples. Values are encoded in (close to) their smallest possible representation in whole octets. This makes DER reasonably easy to decode.

Hence, I replied with

<blockquote class="twitter-tweet" data-conversation="none" data-lang="en"><p lang="en" dir="ltr">The problem with ASN.1 is specific (too many variants of too many types, no guidance when to use which). DER is not the problem.</p>&mdash; Ronald (@blytkerchan) <a href="https://twitter.com/blytkerchan/status/891797275768479744?ref_src=twsrc%5Etfw">July 30, 2017</a></blockquote>
<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

I.e. the problem is in the schema language, which defines innumerable string types which can all be represented in the same way (as an `std::vector`). I as much here: 


<blockquote class="twitter-tweet" data-conversation="none" data-lang="en"><p lang="en" dir="ltr">As to the design issues: the way I see it the designers tried to half-heatedly add semantics to the built-in types with the various strings</p>&mdash; Ronald (@blytkerchan) <a href="https://twitter.com/blytkerchan/status/892081101551927296?ref_src=twsrc%5Etfw">July 31, 2017</a></blockquote>
<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

Before I go much father, I should note that the way I debate things often leaves me arguing for the minority position: I challenge the preposition ruthlessly, relentlessly and fearlessly until it either crumbles or survives. ASN.1 implementations are crappy more often than not, DER decoders are no exception. However, these are implementation issues that are not sure to ASN.1's design. Disregarding X.681, X.682, and X.683, XER, BER, CER, and PER, a safe subset of ASN.1, using X.680 and a subset of X.690, exists.

So, I stopped on the side of the road:

<blockquote class="twitter-tweet" data-conversation="none" data-lang="en"><p lang="en" dir="ltr">OK, so I pulled over and pulled out my iPad (don&#39;t worry: I stopped for my previous tweets also). I said the main issue was tooling, so...</p>&mdash; Ronald (@blytkerchan) <a href="https://twitter.com/blytkerchan/status/892127126392102913?ref_src=twsrc%5Etfw">July 31, 2017</a></blockquote>
<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

and started coding.

Two weeks later, I decided that this might be interesting for this website, so as of now:

- All commits on the master branch will be shown here, with their commit message (updated: due to the way this site is implemented, you'll have to click the "commits" link above to get to the commits)

- I will occasionally post here to explain a few design decisions

- You can ask questions for particular commits in the comments of the corresponding post.

