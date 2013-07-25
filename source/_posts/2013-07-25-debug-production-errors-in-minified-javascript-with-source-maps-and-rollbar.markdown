---
layout: post
title: "Debug Production Errors in Minified JS with Source Maps and Rollbar"
date: 2013-07-25 14:49
comments: true
author: Brian Rue
authorlink: https://plus.google.com/u/1/103254942254370049907/posts
categories: releases
---

[Rollbar](https://rollbar.com) just got a much-requested feature: Source Maps support for Javascript. If you minify your Javascript code in production, this will make debugging production errors much easier. This feature is now live for all accounts.

## What Are Source Maps?

If you minify your Javascript code (i.e. using [UglifyJS2](https://github.com/mishoo/UglifyJS2) or the [Closure Compiler](https://developers.google.com/closure/compiler/)), it gets harder to debug errors. Stack traces reference the line/column numbers in the minified code instead of the original source code.

[Source Maps](http://www.html5rocks.com/en/tutorials/developertools/sourcemaps/) were designed to resolve this; they provide a mapping back from the minified line/column numbers to the original code. Chrome and Firefox have tools to use them in development, but what about errors that happen in production?

## Source Maps and Rollbar

Rollbar can now map stack traces that reference minified code back to the original source files, lines, and column numbers. Here's what a stack trace might have looked like before:

<img src="https://d37gvrvc0wt4s1.cloudfront.net/static/img/blog/stacktrace-minified.png">

Here's the de-minified version:

<img src="https://d37gvrvc0wt4s1.cloudfront.net/static/img/blog/stacktrace-unminified.png">

We'll also use the de-minified stack trace in our [grouping algorithm](https://rollbar.com/docs/guides_grouping/), which should result in more useful grouping.

## Getting this set up

To get started, you'll need to make a change to `_rollbarParams` in the on-page javascript snippet. Add the following two parameters:

``` javascript
_rollbarParams = {
  // ... existing params ...
  // set this to 'true' to enable source map processing
  "client.javascript.source_map_enabled": true,
  // provide the current code version, i.e. the git SHA of your javascript code.
  "client.javascript.code_version": "bdd2b9241f791fc9f134fb3244b40d452d2d7e35"
}
```

Next, either:
- Add a sourceMappingUrl comment at the end of your minified file to point to the source map
- Upload the source map (along with all source files) separately, as part of your deploy process

This second step is a bit more involved so please see our [docs](https://rollbar.com/docs/guides_sourcemaps/) for more details.

## Caveats

All of this relies on having a stack trace with line and column numbers. Unfortunately, browser support for column numbers is inconsistent. As of today, this will work in Chrome, Firefox, and IE10+, and only for caught errors reported like this:

``` javascript
try {
  doSomething();
} catch (e) {
  _rollbar.push(e);
}
```

Uncaught errors (reported via window.onerror) don't have column numbers in any browser we're aware of, so they aren't able to be de-obfuscated. For best results, catch all your exceptions so you don't fall back to the top-level error handler.

Happy debugging and please don't hesistate to contact us ([team@rollbar.com](team@rollbar.com)) if you have any questions.

