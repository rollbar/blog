---
layout: post
title: "Connecting Rollbar with PagerDuty"
date: 2013-10-16 16:11
comments: true
categories: integrations
---

<img src="https://d37gvrvc0wt4s1.cloudfront.net/static/img/blog/pagerduty.png" style="float:right;">

Using Rollbar with [PagerDuty](http://www.pagerduty.com) is now a lot more seamless.  PagerDuty provides SaaS IT on-call schedule management, alerting, and incident tracking.  With our new integration, you can automatically send issues found by Rollbar into incidents in PagerDuty.

We have a few customers using it already. Here's what Richard Lee, CTO at Polydice, a mobile development studio, has to say:

> "With Rollbar's integration of PagerDuty, we're able to get notified as soon as errors detected, and avoid possible downtime to our customers. This powerful combination becomes a must have tool for us." &mdash; Richard Lee, CTO at Polydice

Integrating Rollbar with PagerDuty is easy; just create a new Generic API System in PagerDuty, and then link it in Rollbar's Notification settings. See our [docs](https://rollbar.com/docs/integration/pagerduty/) for detailed instructions.
