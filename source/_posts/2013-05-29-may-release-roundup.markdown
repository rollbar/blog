---
layout: post
title: "May Release Roundup"
date: 2013-05-29 15:30
comments: true
author: Brian Rue
authorlink: https://plus.google.com/u/1/103254942254370049907/posts
categories: releases
---

Here's a roundup of what's new at Rollbar in the month of May.

### Big Features

We revamped our notifications system, and added integrations with a bunch of new services. Rollbar now works with [Asana](http://asana.com), [Campfire](http://campfirenow.com/), [Flowdock](https://flowdock.com), [Github Issues](https://github.com/features/projects/issues), [Hipchat](http://hipchat.com), [JIRA](http://jira.com), [Pivotal Tracker](http://pivotaltracker.com), and [Trello](http://trello.com), as well as any arbitrary system via a [Webhook](http://www.webhooks.org/). See the [announcement blog post](https://rollbar.com/blog/post/2013/05/06/rules-engine-for-notifications-campfire-hipchat-jira-trello/) for more details.

### Small Features

- You can now customize how occurrences are grouped. This first release allows you to define rules of things that should always be grouped together. See the documentation: [Custom Grouping Rules](https://rollbar.com/docs/guides_custom_grouping/). An in-depth post on how to use this is coming soon.

- There's now a "Download CSV" link at the bottom of the Items page, which will let you download a CSV of what you see on the page. Note that this information is also available via our [API](https://rollbar.com/docs/test_console/).
  
  <img src="https://d37gvrvc0wt4s1.cloudfront.net/static/img/blog/download-csv.png">

- You can now sort the Items page by Total Occurrences or Unique Users, in additon to Last Occurrence. Click on the column headers to change the sort.
  
  <img src="https://d37gvrvc0wt4s1.cloudfront.net/static/img/blog/item-list-sort.png">

- Links to files in Github are now linked to the appropriate revision, when this information is available. We'll use one of the following (trying each in order):

  - the value of `server.sha`
  - the value of `server.branch`, if it looks like a SHA
  - the revision from the last deploy before the first occurrence of the item

### Library Updates

#### Ruby

We released [rollbar-gem](https://github.com/rollbar/rollbar-gem) versions 0.9.11 through 0.9.14. The changes include a fix for use with Rails 4, a concurrency bugfix, better support for JSON requests, and the ability to include custom metadata with all reports. See the full [changelog](https://github.com/rollbar/rollbar-gem/blob/master/CHANGELOG.md) for details. To upgrade, change the rollbar line in your Gemfile to:

```ruby
gem 'rollbar', '~> 0.9.14'
```

We also contributed a fix to [resque-rollbar](https://github.com/CrowdFlower/resque-rollbar) to force use of synchronous mode when reporting Resque failures (instead of async mode, which doesn't play nicely with Resque).

#### Python

[pyrollbar](https://github.com/rollbar/pyrollbar) gained a feature and now at version 0.5.7. See the [changelog](https://github.com/rollbar/pyrollbar/blob/master/CHANGELOG.md) for details.

### Bug Fixes

- Fixed an issue where pressing the back button would sometimes cause Chrome to render one of our JSON responses as if it were HTML
- Fixed a bug where removed email addresses could not be re-added

### Documentation Updates

- Added guide on how our [grouping algorithm](https://rollbar.com/docs/guides_grouping/) works.
- Cleaned up our [Items API Reference](https://rollbar.com/docs/api_items/) and fixed a few outdated parts

More is on the way. Stay tuned! And don't forget to send us any feedback: [team@rollbar.com](mailto:team@rollbar.com) &mdash; we love hearing from you.
