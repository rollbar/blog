---
layout: post
title: "Heartbleed Bug Response"
date: 2014-04-08 17:05
comments: true
author: Brian Rue, Cory Virok
authorlink: https://plus.google.com/u/1/103254942254370049907/posts
categories: security
---

## What is Heartbleed?

CVE-2014-0346, known as "Heartbleed", is a bug in OpenSSL v1.0.1 through 1.0.1f that allows a remote attacker to access private memory on the target server. It has existed for almost 2 years. More info can be found here: [http://heartbleed.com/](http://heartbleed.com/)

With this vulnerability, an attacker can:

- Get your private key for your domain's ssl cert
- Decrypt all current and past SSL traffic to/from all affected machines

If this sounds bad, it is. Most sites on the Internet are affected. 

## Are you affected?

Probably. If your web server or load balancer is running on linux and you've updated your packages anytime in the last 2 years,  you are more-than-likely affected. 

To check your OpenSSL version, run `openssl version -a`.

Check out [http://filippo.io/Heartbleed/](http://filippo.io/Heartbleed/) to test your servers for the vulnerability.

## How We Responded

We learned of CVE-2014-0346 at around 4:50pm on 4/7 and immediately began our response. We completed the most important fix (patching OpenSSL) within about an hour, and have been working over the past 24 hours on related issues. 

Here is a timeline of what we've done since the vulnerability was announced:

- 4/7 - 3:01pm - Ubuntu Security Announcements email
    
    Subscribe to this list [here](https://lists.ubuntu.com/mailman/listinfo/ubuntu-security-announce)

- 4/7 - 4:50pm - Began updating our load balancers with the fix. All servers patched by 6pm.

    We're running nginx on Ubuntu 12.04. Updating is as simple as:
        
        apt-get update
        apt-get upgrade
        openssl version -a  # should show that it was built on April 7, 2014
        service nginx restart

    The above didn't work for us on the first try because our servers were talking to a mirror that hadn't updated to the latest packages (after all, they were only a couple hours old). Changing the domain in each line in  `/etc/apt/sources.list` to `archive.ubuntu.com` and then running `apt-get update` again solved this.

- 4/7 - 11pm - rollbar.com and api.rollbar.com SSL certs were rekeyed
    
    We use [DigiCert](http://www.digicert.com/) for our SSL certs. The process was quick and easy.

- 4/7 - 11:10pm - Previous rollbar.com and api.rollbar.com SSL certs revoked

    In order to prevent a possible man-in-the-middle attack we had Digicert revoke our old certs.

- 4/7 - 11:30pm - ratchet.io and submit.ratchet.io rekey requested

    We still support our old domain, ratchet.io which use NetworkSolutions SSL certs

- 4/8 - 11:50am - All rollbar.com cookies were invalidated, forcing users to re-auth

    Since an attacker could have accessed our customers' cookies, we changed the secret key that we use to encrypt cookies. This invalidated all logged-in users' sessions.

- 4/8 - 12:30pm - 2:25pm - All third-party tokens and keys were regenerated and deployed

    We use services like Stripe, Mailgun, Heroku - All required new keys to be generated.

- 4/8 - 3:30pm - ratchet.io and submit.ratchet.io certs were rekeyed and deployed

- 4/8 - 5:30pm - Published this blog post and added in-app notifications to change passwords and cycle access tokens

## Recommended actions for Rollbar Customers

- [Change your password](https://rollbar.com/settings/password/)
- Cycle any access tokens you have used (create and start using a new one, then disable or delete the old one).

    - For projects, go to the project dashboard, then Settings -> Project Access Tokens. Most customers will need to do this.
    - For accounts, go to Account Settings -> Account Access Tokens. Most customers will not need to do this.

### Note for Heroku Users

If you're using Rollbar through Heroku, we've already started the process of cycling your access tokens. We've created new tokens and updated them in your Heroku config. You should update the token in any other locations (i.e. development environments, and anywhere it might  be hardcoded) and then disable/delete the old tokens.

## Closing notes

This was painful, but we're thankful to the security researchers who discovered and responsibly disclosed this issue, and to the security teams at Ubuntu and elsewhere who quickly released patched packages.

If you have any questions, please don't hesitate to contact us at [support@rollbar.com](support@rollbar.com).
