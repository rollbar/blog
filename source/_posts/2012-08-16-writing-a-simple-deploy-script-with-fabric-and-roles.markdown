---
layout: post
title: "Writing a simple deploy script with Fabric and @roles"
date: 2012-08-16 11:52
comments: true
author: Brian Rue
authorlink: https://plus.google.com/u/1/103254942254370049907/posts
categories: deployment articles
---

I first heard about [Fabric](http://www.fabfile.org) a couple years ago while at Lolapps and liked the idea of:

<ul style="margin-left:40px;">
  <li>writing deployment and sysadmin scripts in a language other than Bash</li>
  <li>that language being Python, which we used everywhere else</li>
</ul>

but we already had a huge swath of shell scripts that worked well (and truth be told, Bash isn’t really that bad). But now that we have at clean slate for [Rollbar](https://rollbar.com), Fabric it is.

I wanted a simple deployment script that would do the following:
  
<ol style="margin-left:40px;">
  <li>check to make sure it’s running as the user "deploy" (since that's the user that has ssh keys set up and owns the code on the remote machines)</li>
  <li>for each webserver:
    <ol style="list-style:lower-alpha;margin-left:20px;">
      <li>git pull</li>
      <li>pip install -r requirements.txt</li>
      <li>in series, restart each web process</li>
    </ol>
  </li>
  <li>make an HTTP POST to our <a href="https://rollbar.com/docs/deploys/">deploys api</a> to record that the deploy completed successfully</li>
</ol>

Here’s my first attempt:

{% include_code fabfile1.py %}

Looks close-ish, right? It knows which hosts to deploy to, checks that it’s running as deploy, updates and restarts each host, and records the deploy. Here’s the output:

```
$ sudo -u deploy fab deploy
(env-mox)[brian@dev mox]$ sudo -u deploy fab deploy
[sudo] password for brian: 
[web1] Executing task 'deploy'
[localhost] local: whoami
[web1] run: git pull
[web1] out: remote: Counting objects: 8, done.
[web1] out: remote: Compressing objects: 100% (4/4), done.
[web1] out: remote: Total 6 (delta 4), reused 4 (delta 2)
[web1] out: Unpacking objects: 100% (6/6), done.
[web1] out: From github.com:brianr/mox
[web1] out:    c731b57..1d365e0  master     -> origin/master
[web1] out: Updating c731b57..1d365e0
[web1] out: Fast-forward
[web1] out:  fabfile.py |    8 ++++----
[web1] out:  1 file changed, 4 insertions(+), 4 deletions(-)

[web1] run: pip install -r requirements.txt
[web1] out: Requirement already satisfied (use --upgrade to upgrade): Beaker==1.6.3 in /home/deploy/env-mox/lib/python2.7/site-packages (from -r requirements.txt (line 1))
<snip>
[web1] out: Cleaning up...

[web1] run: supervisorctl restart web1
[web1] out: web1: stopped
[web1] out: web1: started

[web1] run: supervisorctl restart web2
[web1] out: web2: stopped
[web1] out: web2: started

[localhost] local: grep 'rollbar.access_token' production.ini | sed 's/^.* = //g'
[localhost] local: whoami
[localhost] local: git log -n 1 --pretty=format:"%H"
Deploy recorded successfully. Deploy id: 307
[web2] Executing task 'deploy'
[localhost] local: whoami
[web2] run: git pull
[web2] out: remote: Counting objects: 8, done.
[web2] out: remote: Compressing objects: 100% (4/4), done.
[web2] out: remote: Total 6 (delta 4), reused 4 (delta 2)
[web2] out: Unpacking objects: 100% (6/6), done.
[web2] out: From github.com:brianr/mox
[web2] out:    c731b57..1d365e0  master     -> origin/master
[web2] out: Updating c731b57..1d365e0
[web2] out: Fast-forward
[web2] out:  fabfile.py |    8 ++++----
[web2] out:  1 file changed, 4 insertions(+), 4 deletions(-)

[web2] run: pip install -r requirements.txt
[web2] out: Requirement already satisfied (use --upgrade to upgrade): Beaker==1.6.3 in /home/deploy/env-mox/lib/python2.7/site-packages (from -r requirements.txt (line 1))

[web2] out: Cleaning up...

[web2] run: supervisorctl restart web1
[web2] out: web1: stopped
[web2] out: web1: started

[web2] run: supervisorctl restart web2
[web2] out: web2: stopped
[web2] out: web2: started

[localhost] local: grep 'rollbar.access_token' production.ini | sed 's/^.* = //g'
[localhost] local: whoami
[localhost] local: git log -n 1 --pretty=format:"%H"
Deploy recorded successfully. Deploy id: 308

Done.
Disconnecting from web2... done.
Disconnecting from web1... done.
```

Lots of good things happening. But it's doing the whole process -- `check_user`, `update_and_restart`, `rollbar_record_deploy` -- twice, once for each host. The duplicate `check_user` just slows things down, but the duplicate `rollbar_record_deploy` is going to mess with our deploy history, and it's only going to get worse as we add more servers.

Fabric's solution to this, described in their [docs](http://docs.fabfile.org/en/1.4.3/usage/execution.html), is "roles". We can map hosts to roles, then decorate tasks with which roles they apply to. Here we replace the `env.hosts` declaration with `env.roledefs`, decorate `update_and_restart` with `@roles`, and call `update_and_restart` with `execute` so that the `@roles` decorator is honored:

{% include_code fabfile2.py %}

Here's the output:

```
(env-mox)[brian@dev mox]$ sudo -u deploy fab deploy
[sudo] password for brian: 
[localhost] local: whoami
[web1] Executing task 'update_and_restart'
[web1] run: git pull
[web1] out: Already up-to-date.

[web1] run: pip install -r requirements.txt
[web1] out: Requirement already satisfied (use --upgrade to upgrade): Beaker==1.6.3 in /home/deploy/env-mox/lib/python2.7/site-packages (from -r requirements.txt (line 1))
<snip>
[web1] out: Cleaning up...

[web1] run: supervisorctl restart web1
[web1] out: web1: stopped
[web1] out: web1: started

[web1] run: supervisorctl restart web2
[web1] out: web2: stopped
[web1] out: web2: started

[web2] Executing task 'update_and_restart'
[web2] run: git pull
[web2] out: Already up-to-date.

[web2] run: pip install -r requirements.txt
[web2] out: Requirement already satisfied (use --upgrade to upgrade): Beaker==1.6.3 in /home/deploy/env-mox/lib/python2.7/site-packages (from -r requirements.txt (line 1))

[web2] out: Cleaning up...

[web2] run: supervisorctl restart web1
[web2] out: web1: stopped
[web2] out: web1: started

[web2] run: supervisorctl restart web2
[web2] out: web2: stopped
[web2] out: web2: started

[localhost] local: grep 'rollbar.access_token' production.ini | sed 's/^.* = //g'
[localhost] local: whoami
[localhost] local: git log -n 1 --pretty=format:"%H"
Deploy recorded successfully. Deploy id: 309

Done.
Disconnecting from web2... done.
Disconnecting from web1... done.
```

That's more like it. Since `env.hosts` is not set, the undecorated tasks just run locally (and only once), and the `@roles('web')`-decorated task runs for each web host.
