#!/bin/bash

#if you have not installed the module lnr via npm, put the complete path of your lunr module here
DIR=`pwd`
lunr=${DIR}"/lunr.js"

#put the name of your output file here
lunrIndexOutput="index.json"

dir=`readlink -f $1`

entriesFileNames=`mktemp`

find $dir -type f -name "*.html" 2>/dev/null > $entriesFileNames

script="

var lunr = require('$lunr')
var fs = require('fs')
//to account old version of nodejs
fs.existsSync = fs.existsSync || require('path').existsSync;

var idx = lunr(function () {
this.ref('id')
this.field('body')
})

var entries=fs.readFileSync('$entriesFileNames')
var filenames=entries.toString().split('\n')

var entries=filenames.map(function(file){
if(fs.existsSync(file)){
    var data=fs.readFileSync(file)
    idx.add({id: file, body: data.toString()})
}
})

fs.writeFile('$lunrIndexOutput', JSON.stringify(idx), function (err) {
    if (err) throw err
console.log('done')
})
"
node -e "$script"