---
layout: post
title: "Ad-hoc error reporting with Rollbar CLI"
date: 2013-08-08 19:00
comments: true
author: Cory Virok
categories: python tools
---

We just coded up a quick tool to send Rollbar messages from the command line. It's useful for quick, one-off monitoring scripts that you don't have time to instrument with one of our notifiers.

To install, just ```pip install rollbar``` and you're done.

e.g. Tracking all non-500s as WARNINGs from HAProxy

```bash
tail -f /var/log/haproxy.log | awk '{print $11,$0}' | grep '^5' | awk '{$1="";print "warning",$0}' | rollbar -t $ACCESS_TOKEN -e production -v
```

e.g. Watch failed login attempts

```bash
tail -f /var/log/auth.log | grep -i 'Failed password' | awk '{print "error user ",$11,"failed auth from ",$13}' | rollbar -t $ACCESS_TOKEN -e ops
```

More info on how to install and use it can be found [here.](https://github.com/rollbar/pyrollbar/blob/master/README.md#command-line-usage).
