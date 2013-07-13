---
layout: post
title: "Async node.js API server testing"
date: 2013-07-12 1:20
comments: true
author: Cory Virok
authorlink: https://plus.google.com/u/1/103254942254370049907/posts
categories: api testing javascript nodejs articles
---

This post is about how we built our test suite for our API server at [Rollbar](http://rollbar.com/) and some of the tricks and gotchas we ran into along the way. We wanted to build a test suite that not only tested the API logic, but also the underlying code, namely the [Express](http://expressjs.com/) and the [Connect](http://www.senchalabs.org/connect/) middlewares we use. If our API server was going to break, we wanted to know before we deployed it to thousands of customers and millions of requests per day.

Testing is super important. I'm not going to try and work that idea into your head any more than that. If you don't want to test, this probably won't be very helpful/interesting. If you want to learn how to test your API server, read on.

## We use Vows. Why not Mocha?

[Mocha](http://visionmedia.github.io/mocha/) is, by far, the most widely used testing framework for Node.js apps. So, why didn't we use it? The two main reasons were that Vows was the first thing I found when Googling "nodejs async testing" and the other is that I didn't like the syntax of the Mocha tests. Mocha tests are more readble but the benefit of readability was overshadowed by the need to remember all of these new, special-case methods that Mocha injects.

``` javascript
//Mocha
[1,2,3].indexOf(5).should.equal(-1);
```

vs

``` javascript
//Vows
assert.equal([1,2,3].indexOf(5), -1);
```

There's something that bothered me about the former. I didn't like how the library used a bunch of magic to enable something this small/strange.

Mocha has a lot of awesome features but none that were important enough for me to switch.

## A simple Vows test

Vows works just as you'd expect it to, except when it doesn't. More on that later...

``` javascript
var vows = require('vows'); 
var assert = require('assert'); 
vows.describe('testmodule').addBatch({
  "call username() with a valid user id": {
    topic: function() {
      var callback = this.callback;
      return username(42, this.callback);
    },
    "and verify username is correct": function(err, username) {
      assert.isNull(err);
      assert.isString(username);
      assert.equal(username, "cory");
    }
  }
}).export(module, {error: false});
```

The above test will make sure that the function ```username()``` calls its callback with ```(null, "cory")```.

Note that we use this.callback since everything is assumed to be async and we use ```{error: false}``` when we export the batch. More on those later.

Check out the Vows [website](http://vowsjs.org/) for better examples.

## Useful design patterns, (I swear this will be short)

I won't talk much about architecture or design patterns but we've found a few useful idioms that we follow pretty strictly. Doing so has made writing tests super-easy... almost enjoyable, almost.

### Separate your view logic from your API business logic

Your server's views should have one job, to marshall data from the request/socket/carrier pigeon and provide it to your API library.

Any error checking done in your views should be to make sure the types provided to your API library are correct. 

### Make every function you write use a callback.

This is super-important for refactoring and adding new features. If you find yourself wanting to add a feature that requires i/o into a code path that was assumed to be completely synchonous, you'll need to refactor the hell our of your code to make it work. Don't bother. Make everything take a callback. Embrace async!

### Make the first argument to *every* callback be an optional error.

This is how the Node.js developers do it and I agree. It makes for a lot more boiler-plate code but it forces you to keep error handling in-mind when developing. Writing defensive code is more important than writing fewer lines of code.

This will also make testing much, much easier with Vows. How? Read on...

## Testing the API server, for reals

Don't just test your API library; that's kind of lame. Fork a process, start your API server up in it and start firing requests at it using Vows. 

testcommon.js:

``` javascript
exports.initTestingAppChildProc = function(config, promise) {
  // ... Setup temporary config file
  // ... Get path to your main app.js
  // ... Initialize the api library
  
  // fork a child process to start the api server
  var args = [configPath, 'test'];
  var appProc = fork(appJsPath, args);
  
  // This is used to tell if our API server died during its
  // initialization.
  var pendingCallback = true;
  
  appProc.on('message', function(message) {
    if (message == 'ready') {
      pendingCallback = false;
      
      // This is how we know our API server is ready to 
      // receive requests. The message is emitted in the
      // API server once it's ready to receive requests.
      promise.emit('success', null, appProc);
    }
  });
  appProc.on('exit', function(code, signal) {
    if (pendingCallback) {
      var msg = 'child process exited before callback';
      console.error(msg);
      promise.emit('error', new Error(msg));
    }
  });
  appProc.on('SIGTERM', function() {
    process.exit();
  });
};
```

In our API server:

``` javascript
// initialize the API and start the web server when it's ready
api.init(config, function(err) {
  if (err) {
    log.error('Could not initialize API: ' + err);
    process.exit(1);
  } else {
    // Start up the server
    var httpServer = app.listen(port, host, function() {
      log.info('API server is ready.');
      log.info('Listening on ' + host + ':' + port);
    
      // Use the "ready" message to signal that the server is ready.
      // This is used by the test suite to wait for the api server
      // process to start up before sending requests.
      if (process.send) {
        process.send('ready');
      }
    });
  }
});
```

tests/routes.project.js:

``` javascript
vows.describe('routes.project').addBatch({
  // Provides a reference to the api server child process
  'Start up an API server': {
    topic: function() {
      var promise = new events.EventEmitter();
      common.initTestingAppChildProc(config, promise);
      return promise;
    },
    teardown: function(err, childProc) {
      var callback = this.callback;
      var shutdown = function() {
        api.shutdown(callback);
      };
      if (childProc) {
        childProc.on('exit', function(code, sig) {
          shutdown();
        });
        childProc.kill();
      } else {
        shutdown();
      }
    },
    'and get a valid project': {
      topic: function(err, childProc) {
        common.apiGet(url('api/1/project/',
            {access_token: config.test.validEnabledReadAccessToken}), this.callback);
      },
      'returns 200 OK': common.assertStatus(200),
      'returns JSON': common.assertJsonContentType(),
      'fast local response time': common.assertMaxResponseTime(20),
      "returns a valid api response": common.assertValidApiResponse(),
      "has a result key in the JSON response": common.assertJsonHasFields(['result']),
      "there's no api error": common.assertNoApiError(),
      'all of the deploy fields are available': common.assertJsonHasFields(db.projectFields(),
          'result'),
      'cross-check account id with api.getAccount': {
        topic: function(err, resp, body) {
          var project = body.result;
          api.getAccount(body.result.account_id, this.callback);
        },
        'verify the account is not null': function(err, account) {
          assert.isNull(err);      
          assert.isObject(account);         
        }       
      }
    }
}).export(module, {error: false});
```

There is a lot happening in these tests.

- We use promises to notify our test when the API server is ready. 
  - Documentation for using promises with Vows can be found [here](http://vowsjs.org/#-writing-asynchronous-tests).
  - I'm not completely on-board with the Promise design pattern but it seemed like the easiest way to get this working. Mostly, I needed an event to be fired when there was an error that caused the API server process to shut down.
- We use a Vows teardown function to shut down the API server process.
- We use our API library to help test our API server.
  - We cross-check our API server's response by using our API library directly.
- We use Vows macros for reusable tests on all API requests.
  - We also make use of Vows contexts even though there are none in this example.
  - Documentation for macros and contexts are [here](http://vowsjs.org/#-macros).

## Gotchas

Never, ever, ever throw an uncaught exception in a Vows topic. It makes debugging impossible. I've wasted hours looking through my API library for a bug only to find that I had a silly bug in my topic.

Always use ```export(module, {error: false})``` in your Vows batches. This option is not really described in the Vows docs. I had to find it in the source. Basically, if you don't have this, Vows will inspect the first argument to each test to see if it's an error. Vows will potentially call your test functions with a different set of arguments depending on if the first parameter to the topic's callback is an Error or not. It's completely strange and magical and [confusing](https://github.com/cloudhead/vows/pull/263).

Testing without mock objects means that you need a real database which means you probably need real-ish data to test with. This is tough. We chose to maintain a DB SQL fixture that we have to update whenever the schema changes. It's a bit clunky but it works. I'm open to suggestions for this if anyone knows of a better way.

## Wrapping up...

I didn't really go over our testing process much, (maybe in a subsequent blog post) but we use [CircleCI](http://circleci.com) to run all of these tests. It's fast and easy to set up. Also, it has all of the systems that our API server uses like MySQL, Beanstalkd and Memcache pre-installed. This gets us closer to testing in a production environment than we would otherwise be able to get.

Hopefully you were able to glean some useful tips from our experience at [Rollbar](http://rollbar.com/). We love building tools for devs like you!

Add me on Twitter [@coryvirok](https://twitter.com/coryvirok).
Follow [@rollbar](https://twitter.com/rollbar) for more updates.

## Moment of zen

```
✓ OK » 497 honored (33.232s) 
```
