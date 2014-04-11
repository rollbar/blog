---
layout: post
title: "4/10/2014 Processing Delay Postmortem"
date: 2014-04-11 10:48
comments: true
author: Brian Rue, Cory Virok
authorlink: https://plus.google.com/u/1/103254942254370049907/posts
categories: infrastructure, postmortems
---

Yesterday from about 2:30pm PDT until 4:55pm PDT, we experienced a service degradation that caused our customers to see processing delays up to about 2 hours. While no data was lost, alerts were not being sent and new data was not appearing in the rollbar.com interface. Customers instead would see alerts notices on the Dashboard and Items page about the delay.

We know that you rely on Rollbar to monitor your applications and alert you when things go wrong, and we are very sorry that we let you down during this outage.

The service degradation began following some planned database maintenance, which we had expected to have no significant impact on service. 

## The Planned Maintenance

We store all of our data in MySQL in a master-master/active-passive configuration. Yesterday we needed to add partitions to our largest table - a routine procedure. Normally, this process takes about 15 minutes, during which time customers experience small delays in data processing. This process generally goes unnoticed by customers. However, this time something caused the database to load new data extremely slowly which, in turn, caused the outage. 

## Timeline

- 2:06pm - We began the planned maintenance by promoting the passive master to be the new active master.

- 2:29pm - The planned maintenance was complete.
    
    All connections to our old active master were closed and the new active master was getting new data and processing it.

- 2:40pm - It became apparent that new data was being loaded and processed very slowly.
    
    We turned off our data loaders to decrease any contention in the database.

- 2:41pm - We began profiling the slow worker.

- 2:47pm - We tested a theory that a single recurring item was causing most of the slow processing.

- ~2:50pm - We noticed that ping times to the new active master were 1-5 milliseconds - an order of magnitude slower than normal.

- 2:52pm - We turned off replication from the passive to the active database which seemed to help loading data, but not by much.

- ~2:50pm - 3pm

    - The `ALTER` to add partitions completed on the passive database.
        - Up to this point, there were no connections on the passive database.

    - We decided to switch back to the previous active master but quickly reverted after finding that our passive database was missing a significant number of rows.
        - MySQL replication was 0 seconds behind.
        - It was unclear how the passive database thought it was caught up but was missing data.

- ~3:15pm - We identified a the slowest portion of the slow worker, which happened to be unused. We removed this code and deployed to all workers.
    
    - This got processing back to normal speeds and allowed us to begin catching back up.

- ~3:30pm - We turned the data loaders back on.

- 4:30pm - The worker responsible to making new occurrences appear in the interface was caught up, but notifications were still delayed.

- 4:55pm - Everything was caught back up and we were back to 0 delay.


## Follow-on Tasks

We have two open questions:

1.  Why did the data loaders slow down when we switched to the new active master?
2.  How did the databases get out of sync?

We have some theories as to why the data loaders slowed down so much but we are not sure. It could have been the amount of concurrent processes trying to load data into the same table. It could also have been something about the disk layout or cache on the new active master. We plan to investigate serializing loads in general and/or slowly ramping up loads after maintenance in the future.

To determine why our databases became out of sync, we wrote a script to tell us the exact moment when they diverged. Once it completes we will find the coordinates in the new active master's binlogs that correspond with the point in time where the databases became out of sync, then restart replication on the passive master using those coordinates. 

## Conclusion

We take downtime very seriously and we want to be as transparent as possible when it happens. 

We are sorry for the degradation of service and we are working on making sure it doesn't happen again. If you have any questions, please don't hesitate to contact us as [support@rollbar.com](support@rollbar.com)
