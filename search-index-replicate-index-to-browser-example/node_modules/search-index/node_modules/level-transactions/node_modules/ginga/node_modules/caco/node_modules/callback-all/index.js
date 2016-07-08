module.exports = function callbackAll () {
  var result = []
  var finished = false
  var err = null
  var count = 0
  var total = 0
  var callback

  return function next (done) {
    if (typeof done === 'function') {
      callback = done
      // deferred finish callback
      if (!finished && (err || count === total)) callback(err, err ? null : result)
      return
    }
    var curr = total
    total++
    result.push(undefined)

    return function (_err, val) {
      if (finished) return // prevent callback after finished
      if (_err) {
        err = _err
        if (callback) {
          finished = true
          callback(err)
        }
        return
      }
      if (result[curr] !== undefined) return // prevent repeated callback
      result[curr] = val || null
      count++
      if (count === total && callback) {
        finished = true
        callback(null, result)
      }
    }
  }
}
