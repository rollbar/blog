---
layout: post
title: "Real-time Search for Exceptions and Errors"
date: 2012-10-24 11:24
comments: true
author: Brian Rue and Cory Virok
categories: releases
---

We're happy today to announce the release of real-time search. You can now search your exceptions, errors, and log messages by title:

<img src="https://d2tf6sbdgil6xr.cloudfront.net/static/img/blog/realtimesearch1.png">

For exceptions, the title contains the exception class and message. For errors and log messages, it contains the entire message. It’s a full-text search that works best on whole words; we also do a few tricks with camelCase and underscore\_separated terms.

The search index is kept up-to-date in real-time as new items are added to the system (that's the "real-time" part). Typically the delay is ~2 seconds from receiving the input at our API to being in the index and searchable.

Current customers can try it out now; let us know if you run into any issues. What else would you like to see indexed?

If you don't have an account yet, [sign up here for early access](https://rollbar.com/).

## Under the hood

We're using the new [Sphinx](http://sphinxsearch.com/) realtime features for indexing and querying. It's currently running on a single dedicated machine (1 core, 2GB ram, 100GB local disk).

New items are indexed by a long-running script that indexes new items as they are inserted. (It keeps track of its location in the table and polls every second for new rows.) The index includes two full-text *fields*, `title` and `environment`, and two scalar *attributes*, `status` and `level`.

Title and environment don't change, so we don't need to update them. But status (active/resolved) and level (critical/error/warning/info/debug) do. We keep these in sync by simply writing to the search server whenever we update the primary database and whenever we modify our tokenizing algorithm.

Queries are routed through our API server, which returns the paged list of matching item ids that we can then use to filter with on our primary database, (in case the search results are out of date) and fetch the other data necessary for the results page (last occurrence, etc.)

Although our setup is straightforward, there were a few gotchas and lessons learned. 

### Infix queries

Sphinx's realtime index does not currently support infix queries. That means that if you’re searching for "Error" then exceptions with titles like "ReferenceError" or "not\_found\_error" or even "(Error)" would not be found. To get around this, we index both the original title as well as another set of tokens that we’ve determined are useful for the lookup.

e.g. "#462 UnicodeEncodeError: 'latin-1' codec can't encode character u'\\u0441' in position 71: ordinal not in range(256)"

gets tokenized and becomes

"#462 UnicodeEncodeError: 'latin-1' codec can't encode character u'\\u0441' in position 71: ordinal not in range(256) can’t u0441 71 256 Unicode Encode Error latin-1'"

By tacking on these extra tokens, we are able to support most of the relevant infix searches our users are likely to make.

### Sphinx + MySQL

Sphinx search comes with a super-handy feature that lets you connect, add and query the search index using a vanilla MySQL protocol. This is great for debugging and testing but comes with some caveats. 

There are a lot of operations that SphinxQL does not yet support. One of the major ones is the lack of support for "OR" where\_conditions and another is lack of a "COUNT(\*)" method.

Since our API server is written in node, we were able to use the [node-mysql](https://github.com/felixge/node-mysql) library from Felix Geisendörfer. After plugging in the library, we noticed that the Sphinx server drops client connections fairly rigorously so we implemented a layer on top of the node-mysql library to handle reconnects, disconnects, etc... This has been great since it lets us perform maintenance on the Sphinx server without taking down our API server.

### REPLACE

Lastly, we made sure that we were able to re-index our entire database into our Sphinx server by only using the REPLACE command when inserting new items. The docs mention that this can cause memory issues but since it's so infrequent for our use-case, we haven't run into any trouble and the benefit of re-indexing whenever we want more than makes up for it.
