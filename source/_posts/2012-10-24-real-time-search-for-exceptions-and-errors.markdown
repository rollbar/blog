---
layout: post
title: "Real-time Search for Exceptions and Errors"
date: 2012-10-24 11:24
comments: true
author: Brian Rue and Cory Virok
categories: releases
---

We're happy today to announce the release of real-time search. You can now search your exceptions, errors, and log messages by title:

{% img http://brian.ratchetdev.com/static/img/blog/realtimesearch1.png %}

For exceptions, the title contains the exception class and message. For errors and log messages, it contains the entire message. It’s a full-text search that works best on whole words; we also do a few tricks with camelCase and underscore\_separated terms.

The search index is kept up-to-date in real-time as new items are added to the system (that's the "real-time" part). Typically the delay is ~2 seconds from receiving the input at our API to being in the index and searchable.

Current customers can try it out now; let us know if you run into any issues. What else would you like to see indexed?

If you don't have an account yet, [sign up here for early access](https://ratchet.io/).

## Under the hood

We're using [Sphinx](http://sphinxsearch.com/) for indexing and querying. It's currently running on a single dedicated machine (1 core, 2GB ram, 100GB local disk).

New items are indexed by a long-running script that indexes new items as they are inserted. (It keeps track of its location in the table and polls every second for new rows.) The index includes two full-text *fields*, `title` and `environment`, and two scalar *attributes*, `status` and `level`.

Title and environment don't change, so we don't need to update them. But status (active/resolved) and level (critical/error/warning/info/debug) do. We keep these in sync by simply writing an to the search server whenever we update the primary database.

Queries are routed through our API server, which returns the paged list of matching items. This list is then used for a database query where we re-filter the results (in case the search results are out of date) and fetch the other data necessary for the results page (last occurrence, etc.).

