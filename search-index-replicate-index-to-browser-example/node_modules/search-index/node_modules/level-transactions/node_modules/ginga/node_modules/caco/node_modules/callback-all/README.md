# callback-all

Aggregate all callback sequence into one array result.

[![Build Status](https://travis-ci.org/cshum/callback-all.svg?branch=master)](https://travis-ci.org/cshum/callback-all)

```bash
npm install callback-all
```

```js
var callbacks = require('callback-all')

var all = callbacks()

asyncFn1(all()) // foo
asyncFn2(all()) // bar
asyncFn3(all()) // hello
asyncFn4(all()) // world

all(function (err, result) {
  // return err if any of them error
  // result array followed by all() sequence
  console.log(result) // ['foo', 'bar', 'hello', 'world']
})

```

`yield` parallel callbacks in [caco](https://github.com/cshum/caco):

```js
var caco = require('caco')
var callbacks = require('callback-all')


caco(function * (next) {
  asyncFn1(all()) // foo
  asyncFn2(all()) // bar
  asyncFn3(all()) // hello
  asyncFn4(all()) // world

  var result = yield all(next)

  console.log(result) // ['foo', 'bar', 'hello', 'world']

})(function (err) {
 // handle thrown error
})

```
