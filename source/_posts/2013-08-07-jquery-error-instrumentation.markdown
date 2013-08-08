---
layout: post
title: "jQuery Error Instrumentation"
date: 2013-08-08 11:18
comments: true
author: Sergei Bezborodko
categories: releases javascript
---

Today we are releasing a new feature for our JavaScript notifier that should make tracking down errors much easier if you use jQuery 1.7 and above. The new functionality comes in a separate JS plugin snippet that should be placed right below where jQuery is loaded. Here is the first version of the plugin:

```html
<script>
!function(r,n,e){var t={"notifier.plugins.jquery.version":"0.0.1"};n._rollbar.push(
{_rollbarParams:t});r(e).ajaxError(function(r,e,t,u){var o=e.status;var a=t.url;
n._rollbar.push({level:"warning",msg:"jQuery ajax error for url "+a,jquery_status:o,
jquery_url:a,jquery_thrown_error:u,jquery_ajax_error:true})});var u=r.fn.ready;
r.fn.ready=function(r){return u.call(this,function(){try{r()}catch(e){
n._rollbar.push(e)}})};var o={};var a=r.fn.on;r.fn.on=function(r,e,t,u){
var f=function(r){var e=function(){try{return r.apply(this,arguments)}catch(e){
n._rollbar.push(e);return null}};o[r]=e;return e};if(e&&typeof e==="function"){
e=f(e)}else if(t&&typeof t==="function"){t=f(t)}else if(u&&typeof u==="function"){
u=f(u)}return a.call(this,r,e,t,u)};var f=r.fn.off;r.fn.off=function(r,n,e){
if(n&&typeof n==="function"){n=o[n];delete o[n]}else{e=o[e];delete o[e]}
return f.call(this,r,n,e)}}(jQuery,window,document);
</script>
```

The source can be found on GitHub [here](https://github.com/rollbar/rollbar.js/blob/master/src/plugins/jquery.js).

The snippet wraps the `ready()`, `on()` and `off()` functions in jQuery to wrap any passed-in handlers in try/except blocks to automatically report errors to Rollbar. This lets us collect the full stack trace with line and column numbers for each frame, instead of just the last frame with only a line number. When combined with [source maps](https://rollbar.com/docs/guides_sourcemaps/), this makes debugging JavaScript errors much more doable.

The new snippet also adds a handler to ajaxError() to automatically report any jQuery AJAX errors such as 404s and 500s to Rollbar. If you don't want this, add the following option to your base snippet's `_rollbarParams`:
```
"notifier.plugins.jquery.ignoreAjaxErrors": true
```
You can start tracking errors in Rollbar by [signing up for free](https://rollbar.com/signup). Or read more in the [docs](https://rollbar.com/docs/notifier/rollbar.js).
