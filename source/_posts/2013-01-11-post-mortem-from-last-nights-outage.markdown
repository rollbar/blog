---
layout: post
title: "Post-mortem from last night's outage"
date: 2013-01-11 15:57
comments: true
author: Brian Rue
categories: postmortems infrastructure
---

> *Tl;dr: from about 9:30pm to 12:30am last night, our website was unreachable and we weren't sending out any notifications. Our API stayed up nearly the whole time thanks to an automatic failover.*

We had our first major outage last night. We want to apologize to all of our customers for this outage, and we're going to continue to work to make the [Ratchet.io](http://ratchet.io) service stable, reliable, and performant.

What follows is a timeline of events, and a summary of what went wrong, what went right, and what we're doing to address what went wrong.

## Background

First some background: our infrastructure is currently hosted at Softlayer and layed out like this (simplified):

<img src="https://d2tf6sbdgil6xr.cloudfront.net/static/img/blog/infrastructurediagram.png">

That is:

- our primary cluster of servers is in San Jose
- all web traffic (ratchet.io / www.ratchet.io) is handled by lb2
- all API traffic (submit.ratchet.io) is handled by lb1
- lb3 (in Singapore) and lb4 (Amsterdam) are ready to go but not in use yet (more on this below), providing failover and faster API response times to customers outside of the Americas.

We've been in the process of setting up lb3 and lb4, along with some [fancy DNS functionality](http://dyn.com/dns/dynect-managed-dns/) from Dyn, to provide redundancy and faster response times to our customers outside of the Americas. Each is running a stripped-down version of our infrastructure, including:

- a frontend web server (nginx)
- two instsances of our node.js API server
- a partial database slave (for validating access tokens)
- our offline loading process (soon to be open-sourced!), for doing async writes to the active master database.

Switching DNS to Dyn requires changing the nameservers, which can take "up to 48 hours". At the start of this story, it's been about 36 hours. To play it safe, after testing out Dyn on a separate domain, we configured it to have the same settings as we had before -- lb3 and lb4 are not in play yet.

## Timeline

Now the (abbreviated) timeline. All times are PST.

<div style="padding-left:2em;">
<p>9:30pm: Cory got an alert from Pingdom that our website (ratchet.io) was down. He tried visiting it but it wouldn't load (just hung). Remembering the pending DNS change, he immediately checked DNS propagation and saw that ratchet.io was pointing at the wrong load balancer -- lb1 (the API tier), not lb2.

<p>Cory and Sergei investigated. The A record for ratchet.io showed as correct in Dyn, but DNS was resolving incorrectly.

<p>9:47pm: Cory and Sergei looked at <a href="http://twitter.com/SoftlayerNotify" target="_blank">@SoftlayerNotify</a> and saw that there was an issue underway with one of the routers in the San Jose data center.

<p>9:49pm: Website accessible by its IP address.

<p>9:51pm: No longer accessible by IP.

<p>10:05pm: Twitter search for "softlayer outage" shows other people being affected.

<p>10:05pm: API tier (submit.ratchet.io) appears to be working. Sergei verifies that it's hitting lb3 (in Singapore).
</div>

You might notice that we said before that lb3 wasn't supposed to be in service yet. What appeared to have happened DNS had automatically failed over to lb3 (since lb1 was down because of the Softlayer outage). We had set something like this up before when testing out Dyn, but it wasn't supposed to be active yet. Fortunately, lb3 was ready to go and handled all of our API load just fine.

<div style="padding-left:2em;">
<p>10:22pm: Sergei tries fiddling with the Dyn configuration to see if anything helps.

<p>10:35pm: Sergei starts trying to get ahold Dyn

<p>10:58pm: Softlayer posts that "13 out of 14 rows of servers are online". We must be in the 14th, because we're still unreachable at this point. Brian tries hard-rebooting the 'dev' server to see if it helps. It doesn't.

<p>11:15pm: Sergei gets a call from Dyn, who tells him that the problem was a "stale Real-Time Traffic Manager configuration" and they're looking into it.

<p>11:54pm: @SoftlayerNotify posts that "all servers are online however some intermittent problems remain"

<p>11:55pm: Sergei notices that the A record for ratchet.io in the Dyn interface appears to have been deleted, and he can't add it back.

<p>12:00am: Brian sees that ratchet.io is working again. Cory notices that API calls are hitting lb2, causing them to hit the old, non-optimized API handling code on our web tier, overloading them and causing the website to hang. Frequent process restarts minimize the impact.

<p>12:19am: Sergei gets an email back from Dyn saying that they're still looking into the problem.

<p>12:28am: Dyn calls to say they were able to fix everything. Sergei confirms. lb3 and lb4 are now fully utilized.

<p>12:42am: Brian tweets that all systems are stable.

<p>2:58am: Softlayer tweets that they're about to run some code upgrades on the troubled router, which will cause some public network disruption.

<p>4:00am:- A customer reports connectivity issues to ratchet.io

<p>4:10am: Softlayer tweets that the troubled router is finally stable.
</div>

## So what happened here?

1. Softlayer experienced a network outage, causing our servers in San Jose to be intermittently, then fully, unreachable
2. This triggered a DNS failover controlled by a stale Dyn configuration, which cascaded into a broken set of DNS records
3. After about 3 hours, our San Jose servers came back online, and about 30 minutes after that, the DNS issue was resolved.


## What went right

- We were notified of the problem by our backup monitoring service, Pingdom. (We're using Nagios as our primary, but it runs inside of San Jose.)
- Dyn's DNS failover did work, even though wasn't really supposed to be turned on. Our logs don't show any large gaps in customer data being received.
- A single machine (lb3) was able to handle all of our API traffic during the outage.
- The API tier was able to handle a master-offline situation.
- When San Jose came back online, data processing quickly caught up, notifications were sent, and the system was stable.
- Our team came together, stayed mostly calm, and did everything we reasonably could to restore service as quickly as possible.

As a bonus, our Singapore and Amsterdam servers are [now in service](http://www.whatsmydns.net/#A/submit.ratchet.io).

## What went wrong

- Parts of our service were unusable for a long period of time
  - Notifications for new errors, etc. weren't sent
  - The web app didn't load, and there was no maintenance page.
  - [status.ratchet.io](http://status.ratchet.io) didn't show useful information
- Even though the Softlayer private network was at least partially accessible, we couldn't access it because we only had one way in ('dev', in San Jose).
- The web tier got crushed trying to handle the API load with its old code.

## Action items

In the short term (most of this will get done today):

<div style="padding-left:2em;">
<p><i>1b.</i> Set up a web server in a separate datacenter to serve a maintenance page.

<p><i>1c.</i> Add meta-level checks to status.ratchet.io. It currently gets data pushed from Nagios, but this isn't helpful when San Jose is entirely unreachable.

<p><i>2.</i> Add another 'dev'-like machine that we can use to administer servers, deploy code, etc. if San Jose is unreachable

<p><i>3.</i> Remove that old code, and make it an error if any API traffic hits the web tier.
</div>

And longer term:

<div style="padding-left:2em;">
<p><i>1a.</i> Add a host master standby in another datacenter for fast failover. If an episode like last night's happens again, this will let us get notifications back online in a few minutes instead of a few hours.

<p><i>1b.</i> Set up a read-only web tier in another datacenter
</div>

## Conclusion

We hope this was, if nothing else, an interesting look into our infrastructure, and to the journey of building a highly-available we service. 

If you have any questions about the outage or otherwise, let us know in the comments or email us at support@ratchet.io
