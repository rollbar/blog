---
layout: post
title: "Rollbar launches, raises initial funding"
date: 2013-02-26 12:15
comments: true
author: Brian Rue
categories: announcements
---

Today we’re excited to announce the public launch of Rollbar. Rollbar tracks and analyzes errors in production applications, helping dev and ops teams diagnose and fix them.

### Platform-agnostic API

Anything that can speak JSON and HTTP can talk to Rollbar. Our API accepts raw "items" (errors, exceptions, and log messages) and deploys as inputs, and aggregated items, occurrences, and deploys as outputs. We provide official libraries for Ruby, Python, PHP, Node.js, Javascript, and Flash; or you can [roll your own](https://rollbar.com/docs/api_items/).

### Severity levels

Just because something raises an exception, doesn't mean it should be treated as an "error". Rollbar lets you utilize five severity levels (from "debug" to "critical") to control visibility and notifications. Severity can be set in your code, or after-the-fact in the Rollbar interface.

### Track users through your stack

Person tracking helps you provide great customer support by emailing affected users when you fix an error they hit. Or see the history for a particular user and link customer error reports to code problems, client- and server-side.

### So much more

API endpoints on 3 continents. Resolving and reactivations. Real-time notifications for new issues. Graphs everywhere. Deploy tracking. Search by title, host, file, context, date, severity, status. Replay an issue by pressing a button. SSL everywhere. Github, Asana, and Pivotal Tracker integration. 

We've built many of the pieces our beta customers have needed, and we really think you're going to like it. [Start a free trial now](https://rollbar.com/signup/), or see [pricing](https://rollbar.com/pricing), [features](https://rollbar.com/features/), or [docs](https://rollbar.com/docs/).

### More firepower

We're also excited to announce that we've raised an initial round of funding from some of the smartest people in the business. Mike Hirshland (Resolute.vc), Hiten Shah (KISSmetrics), and Arjun Sethi participated in the round. This funding gives us some extra firepower to grow the team and bring our vision to life.

We’re really excited and can’t wait to keep making Rollbar better!

Brian, Cory, and Sergei
