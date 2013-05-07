---
layout: post
title: "Rules Engine for Notifications, Plus Integrations with Campfire, Hipchat, JIRA, and Trello"
date: 2013-05-06 21:30
comments: true
categories: releases
---

Tonight we're revamping the model for defining what you want to be notified about from Rollbar. Rollbar now integrates with Asana, Campfire, Github Issues, Hipchat, JIRA, Pivotal Tracker, and Trello, as well as any arbitrary system via our Webhook.

## New Integration Channels

In addition to our existing channels (Email, Asana, Github Issues, Pivotal Tracker, and Webhook), we're launching support for four more: Campfire, Hipchat, JIRA, and Trello. You can set up all of this in Settings -> Notifications.

## Notification Rules Engine

Notifications are now configured per-project (instead of per-user-per-project), using a trigger-action model. There are triggers for the following events:

- New Item (first occurrence of a new issue)
- Reactivated Item (a previously resolved issue has occurred again)
- 10^nth Occurrence (an issue has occurred for the 10th, 100th, etc. time)
- Resolved Item (an item has been resolved by hand)
- Reopened Item (an item has been reopened by hand)
- Post-deploy (you've notified us that you deployed a new release)

Corresponding actions are available for most actions in most channels. If it would make sense, it probably exists.

Most actions can be configured as you'd expect (i.e. set which teams should receive an email, or which user to assign JIRA issues to).

Item-related triggers can be filtered by environment, level, title (exception class+message), and filename. Deploy triggers can be filtered by environment and comment. Our underlying tech supports much more than the UI exposes, so let us know what other filters you'd like to see.

## Migration for existing customers

We've migrated existing customers' settings to the new system, but there were a few aspects that didn't map very well (i.e. per-user-per-project settings). We hope the new system will work better more most use-cases, but let us know if there's something you are having trouble setting up.

## Questions? Feedback?

Let us know if you have any questions about how to get the notifications you want. We look forward to your feedback. What other integrations do you want? Let us know in the comments.

