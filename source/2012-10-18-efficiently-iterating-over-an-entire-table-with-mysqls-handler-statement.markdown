---
layout: post
title: "Efficiently iterating over an entire table with MySQL's HANDLER statement"
date: 2012-10-18 12:28
comments: true
categories: mysql, python
---

From time to time, you may need to read the entire contents of a large table. A few cases we've run into:

- doing data migrations, especially when the data is unstructured (i.e. json stored in a TEXT column)
- backfilling data that is normally extracted during initial processing 
- (stats scripts aj used to run)
- ... others ...




