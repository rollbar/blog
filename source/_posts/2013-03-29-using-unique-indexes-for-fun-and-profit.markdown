---
layout: post
title: "Taking UNIQUE indexes to the next level"
date: 2013-03-29 09:15
comments: true
categories: articles
---

You've probably seen unique constraints somewhere -- either in Rails' [`validates :uniqueness`](http://guides.rubyonrails.org/active_record_validations_callbacks.html#uniqueness), Django's [`Field.unique`](https://docs.djangoproject.com/en/dev/ref/models/fields/#unique), or a raw SQL [table definition](http://dev.mysql.com/doc/refman/5.5/en/create-index.html). The basic function of unique constraints (preventing duplicate data from being inserted) is nice, but they're so much more powerful than that. When you write INSERT or REPLACE statements that rely on them, you can do some pretty cool (and efficient) things that you would've had to do multiple queries for otherwise.

This post covers unique indexes in MySQL 5.5. Other versions of MySQL are similar. I'm not sure about Postgres or other relational databases but presume they're similar-ish as well.

## Primer: what is a unique index?
Pre-primer: data in a database is stored on disk somewhere. In a SQL database, the data is organized into tables which have rows and columns. An index is a way to look up particular rows, based on the values of one or more columns, without having to scan through the whole table. Instead, you look up those values in the index, which tells you where to find the matching rows. 

Index lookups are typically faster than full table scans because they're organized for fast searches on the indexed columns (usually using binary trees), and they're also generally smaller than the original data.

A unique index is an index that also imposes a constraint: that no two entries in the index can have the same values. It can be comprised of one column or many columns. If many columns, then the entire tuple of columns is used for determining uniqueness. There can be other columns in the table that are not part of the index; these don't affect the constraint.

Primary keys are a special case of unique index; we'll cover this in more detail later.

Unique indexes can be created in a CREATE TABLE statement like this 123123:

``` sql
CREATE TABLE user (
  username varchar(32),
  password char(32),
  unique (username)
);
```

or using an ALTER TABLE statement like this:

``` sql
ALTER TABLE users ADD unique (username);
```

## What does a unique constraint affect?

A unique constraint prevents you from changing your data in a way that would result in having duplicate data in the index. For example, given the above 'user' table, the following will happen if we try to insert duplicate data:

```
mysql> INSERT INTO user VALUES ('brian', PASSWORD('asdf'));
Query OK, 1 row affected, 1 warning (0.04 sec)

mysql> INSERT INTO user VALUES ('brian', PASSWORD('asdfjkl'));
ERROR 1062 (23000): Duplicate entry 'brian' for key 'username'
```

or if we try to get duplicate data with an update:

```
mysql> INSERT INTO user VALUES('sherlock', PASSWORD('123456'));
Query OK, 1 row affected, 1 warning (0.00 sec)

mysql> UPDATE user SET username = 'brian' WHERE username = 'sherlock';
ERROR 1062 (23000): Duplicate entry 'brian' for key 'username'
```

So we can see that unique indexes are a great way to maintain consistency of our data at the database level. If two people try to sign up with the same username, for example, the database will reject it and return a duplicate key error.

## Taking it to the next level

MySQL provides several commands, all variations of INSERT, that can take advantage of unique indexes by specifying what to do (instead of erroring) when the insert would result in a duplicate. These are best illustrated by example.

### INSERT ... ON DUPLICATE KEY UPDATE
Let's say we're building a simple ad impression tracking system. Ads are served by web servers and the impression counts are tracked in a database. We just want to know the number of ad impressions each hour. So we make a table like this:

```
CREATE TABLE hour_impression (
  hour int unsigned not null,  -- number of hours since unix epoch
  impressions int unsigned not null default 0,
  primary key(hour)
);
```

Side note: here we're using `hour` as the primary key, rather than having an auto-increment primary key like before in the 'user' table. This guarantees that `hour` is unique (since primary keys are a subset of unique keys), and has a nice property of laying out the data on disk in hour-order.

A naive algorithm for recording each impression would be to:

1. Check if a row already exists for the hour
2. If not: `INSERT INTO hour_impression (hour, impressions) VALUES (:hour, 1)`
3. If so: `UPDATE hour_impression SET impressions = impressions + 1 WHERE hour = :hour`

But this exposes a race condition: what happens if two impressions happen at approximately the same time, on two different web servers? It's possible that both will try to INSERT, and the second one is going to fail (because of the unique constraint).

What we want to do is combine the above algorithm into a single step. This is what INSERT … ON DUPLICATE KEY UPDATE is for:

```
INSERT INTO hour_impression (hour, impressions)
VALUES (379015, 1)
ON DUPLICATE KEY UPDATE impressions = impressions + 1
```

Now that it's a single step, we can run as many of these statements in parallel as we want, and the database will take care of the concurrency issues for us. Sweet!

### INSERT IGNORE
Now let's say instead of counting the number of impressions in each hour, we just want to know which minutes any impressions at all were shown. So we create a table like this:

```
CREATE TABLE minute_impression (
  minute int unsigned not null,  -- number of minutes since the unix epoch
  primary key (minute)
);
```

Similar to before, a naive algorithm for recording which minutes had any impressions would be to:

1. Check if a row already exists for the minute
2. If so, do nothing
3. If not, `INSERT INTO minute_impression (minute) VALUES (:minute)`

This has the same kind of race condition as in the previous example. INSERT IGNORE exists to combine all of this into a single step:

```
INSERT IGNORE INTO minute_impression (minute) VALUES (22740922)
```

And as before, now we can run as many of these in parallel as we want and let the database take care of the concurrency.

## More tricks

### REPLACE
The opposite of INSERT IGNORE. Overwrites matching rows with the new data instead of discarding it.

### Nullable unique indexes
Values in a unique index have to be unique, but there's an exception: NULLs don't count. For example, let's say you let people pick their username after signup. You might have table like:

```
CREATE TABLE user (
  id int unsigned not null auto_increment,
  username varchar(32) default null,
  unique (username),
  primary key (id)
);
```

You can have as many users as you like who haven't chosen a username (it'll be NULL) while still preventing multiple users from having the same username.

### VALUES() in the ON DUPLICATE KEY UPDATE clause
You can insert multiple rows in a single INSERT … ON DUPLICATE KEY UPDATE statement, and the UPDATE rule will apply for each row that would've been a duplicate. In some cases you'll want the update statement to reflect the values of each particular row, and that's not possible to do by hardcoding them in the statement.

For example, let's return to the ad impression tracking problem from before, with this hour_impression table:

```
CREATE TABLE hour_impression (
  hour int unsigned not null,  -- number of hours since unix epoch
  impressions int unsigned not null default 0,
  primary key(hour)
);
```

But now instead of recording impressions one at a time, we're batching them so that each INSERT increments `impressions` by a value 1 or higher. If we insert one of these batches at a time, we can do:

```
INSERT INTO hour_impression (hour, impressions)
VALUES (379015, 23)  -- 23 impressions during 12am 3/28/2013
ON DUPLICATE KEY UPDATE
impressions = impressions + 23
```

If we want to insert multiple rows in the same statement, there's a problem -- the amount in the UPDATE clause is hardcoded. We can fix this using VALUES() to reference the value from the would-have-been-inserted row:

```
INSERT INTO hour_impression (hour, impressions)
VALUES (379015, 23), (379015, 55)
ON DUPLICATE KEY UPDATE
impressions = impressions + VALUES(impressions)
```

## Conclusion

Unique indexes are useful when used alone and become incredibly powerful when used in combination with INSERT ... ON DUPLICATE KEY UPDATE and its variants. We make heavy use of this at [Rollbar](https://rollbar.com) and it works great.

Questions? Corrections? Let me know in the comments.

### References

1. [INSERT ... ON DUPLICATE KEY UPDATE syntax](http://dev.mysql.com/doc/refman/5.0/en/insert-on-duplicate.html)
2. [INSERT IGNORE syntax](http://dev.mysql.com/doc/refman/5.0/en/insert.html) (ctrl+f on the page)
3. [REPLACE syntax](http://dev.mysql.com/doc/refman/5.0/en/replace.html)
