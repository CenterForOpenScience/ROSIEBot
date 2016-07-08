var test = require('tape')
var cbAll = require('./')

function cbRes (timeout, res, cb) {
  setTimeout(cb.bind(null, null, res), timeout)
}
function cbErr (timeout, err, cb) {
  setTimeout(cb.bind(null, err), timeout)
}

test('callback all', function (t) {
  t.plan(2)
  var next = cbAll()
  cbRes(20, 1, next())
  cbRes(10, 2, next())
  cbRes(30, 3, next())
  cbRes(0, 4, next())
  next(function (err, res) {
    t.notOk(err, 'no error')
    t.deepEqual(res, [1, 2, 3, 4], 'callback all correct sequence')
  })
})
test('callback error', function (t) {
  t.plan(2)
  var next = cbAll()
  cbRes(20, 1, next())
  cbErr(10, 2, next())
  cbRes(30, 3, next())
  cbErr(0, 4, next())
  next(function (err, res) {
    t.equal(4, err, 'only return first error callback')
    t.notOk(res, 'no result on error')
  })
})
test('repeated callback', function (t) {
  t.plan(2)
  var next = cbAll()
  cbRes(20, 1, next())
  var cb = next()
  cbRes(10, 2, cb)
  cbRes(11, 'foo', cb)
  cbRes(12, 'bar', cb)
  cbRes(30, 3, next())
  cbRes(0, 4, next())
  next(function (err, res) {
    t.notOk(err, 'no error')
    t.deepEqual(res, [1, 2, 3, 4], 'callback all correct sequence')
  })
})
test('callback before done', function (t) {
  t.plan(2)
  var next = cbAll()
  cbRes(20, 1, next())
  cbRes(10, 2, next())
  cbRes(30, 3, next())
  cbRes(0, 4, next())
  setTimeout(function () {
    next(function (err, res) {
      t.notOk(err, 'no error')
      t.deepEqual(res, [1, 2, 3, 4], 'callback all correct sequence')
    })
  }, 100)
})
test('no callback after done', function (t) {
  t.plan(2)
  var next = cbAll()
  cbRes(20, 1, next())
  cbRes(10, 2, next())
  cbRes(30, 3, next())
  setTimeout(function () {
    cbRes(0, 4, next())
    next(function (err, res) {
      t.notOk(err, 'no error')
      t.deepEqual(res, [1, 2, 3, 4], 'callback all correct sequence')
    })
    setTimeout(function () {
      cbRes(20, 1, next())
      cbRes(10, 2, next())
      cbRes(30, 3, next())
      cbRes(0, 4, next())
    }, 100)
  }, 100)
})
