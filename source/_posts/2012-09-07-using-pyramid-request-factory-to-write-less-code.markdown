---
layout: post
title: "Using a Request Factory in Pyramid to write a little less code"
date: 2012-09-07 11:00
comments: true
author: Brian Rue
categories: pyramid articles
---

At [Ratchet.io](http://ratchet.io/), we've been using [Pyramid](http://www.pylonsproject.org/) as our web framework and have been pretty happy with it. It's lightweight and mostly stays out of our way. 

Pyramid doesn't have a global request object that you can just import [1], so it makes you pass around `request` wherever you need it. That results in a lot of library code that looks like this:

```python
# lib/helpers.py
def flash_success(request, body, title=''):
    request.session.flash({'body': body, 'title': title'})
```

and a lot of view code that looks like this:

```python
# views/auth.py
@view_config(route_name='auth/login')
def login(request):
    # (do the login...)
    helpers.flash_success(request, "You're now logged in.")
    # (redirect...)
```

That is, there ends up being a lot of function calls that pass `request` as their first argument. Wouldn't it be nicer if we could attach these functions as methods on `request` itself? That would save a few characters every time we call them, and let us stop thinking about whether `request` is the first or last argument. Pyramid facilitates this by letting us provide our own [Request Factory](http://pyramid.readthedocs.org/en/latest/narr/hooks.html#changing-the-request-factory):

```python
from pyramid.request import Request

class MyRequest(Request):
    def hello(self):
        print "hello!"

def main(global_config, **settings):
    config = Configurator(settings=settings, request_factory=MyRequest)
    # ...
```

Now the `request` passed to our view methods, and everwhere else in our app, has our `hello` method.

So, what can we do with this that's actually useful? In our codebase, we have a few convenience methods to get data about the logged-in user, flash messages, and check if features are enabled. 

Here it is, unedited, in its entirety:

```
class MoxRequest(pyramid.request.Request):
    # logged-in-user access
    @util.CachedAttribute
    def user_id(self):
        from pyramid.security import authenticated_userid
        user_id = authenticated_userid(self)
        log.debug('authenticated user id: %r', user_id)
        return user_id

    @util.CachedAttribute
    def user(self):
        user_id = self.user_id
        if user_id:
            return model.User.get(user_id)
        return None

    @util.CachedAttribute
    def username(self):
        if self.user:
            return self.user.username
        else:
            return None

    def gater_check(self, feature_name):
        return self.registry.settings.get('gater.%s' % feature_name) == 'on'

    # flash methods
    def flash_success(self, body, title=''):
        self._flash_message(body, title=title, queue='success')

    def flash_info(self, body, title=''):
        self._flash_message(body, title=title, queue='info')

    def flash_warning(self, body, title=''):
        self._flash_message(body, title=title, queue='warning')

    def flash_error(self, body, title=''):
        self._flash_message(body, title=title, queue='error')

    def _flash_message(self, body, title='', queue=''):
        self.session.flash({'title': title, 'body': body}, queue=queue)
```

This just sits in our top-level `__init__.py`, along with the `main()` entry point. 

Notes: `@util.CachedAttribute` contains [this recipe](http://code.activestate.com/recipes/276643-caching-and-aliasing-with-descriptors/). "Mox" is an easy-to-type codename, named after [these mountains](http://www.summitpost.org/mox-peaks-from-red-face-mountain/690027).

[1] I'm still not sold on this, but I'm getting by. It arguably causes problems with testing and such, but it *is* pretty nice to magically `from flask import request`.
