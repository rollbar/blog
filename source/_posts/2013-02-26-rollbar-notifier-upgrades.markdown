---
layout: post
title: "Upgrading to the new Rollbar notifier libraries"
date: 2013-02-26 17:25
comments: true
author: Sergei Bezborodko
categories: notifiers
---

We've updated all of our notifier library repositories to match the name change to Rollbar today. The old Ratchet.io repos have been deprecated and all further development will continue on the respective Rollbar versions.

Please note that the `submit.ratchet.io` endpoint and the existing libraries will continue to work for the indefinite future, so you don't have to do anything right now. But we do recommend upgrading to take advantage of future updates.

Upgrading *should* be seamless and quick. Please contact [support@rollbar.com](mailto:support@rollbar.com) if you run into any issues.

Here are links to the upgrade instructions for each:

 - Browser JS - update the JS snippet used on your site to the version shown [here](http://rollbar.com/docs/)

 - [pyratchet](https://github.com/rollbar/pyrollbar/blob/master/UPGRADE_FROM_RATCHET.md)

 - [ratchetio-gem](https://github.com/rollbar/rollbar-gem/blob/master/UPGRADE_FROM_RATCHET.md)

 - [ratchetio-php](https://github.com/rollbar/rollbar-php/blob/master/UPGRADE_FROM_RATCHET.md)

 - [ratchet-agent](https://github.com/rollbar/rollbar-agent/blob/master/UPGRADE_FROM_RATCHET.md)

 - [node_ratchet](https://github.com/rollbar/node_rollbar/blob/master/UPGRADE_FROM_RATCHET.md)

 - [flash_ratchet](https://github.com/rollbar/flash_rollbar/blob/master/UPGRADE_FROM_RATCHET.md)

