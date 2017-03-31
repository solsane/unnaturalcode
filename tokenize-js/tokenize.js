'use strict';
const fs = require('fs');
const esprima = require('esprima');
const mmap = require('mmap');
function removeShebangLine(source) {
  return source.replace(/^#![^\\r\\n]+/, '');
}
/*
  Adapted from: http://esprima.org/demo/parse.js

  Copyright (C) 2013 Ariya Hidayat <ariya.hidayat@gmail.com>
  Copyright (C) 2012 Ariya Hidayat <ariya.hidayat@gmail.com>
  Copyright (C) 2011 Ariya Hidayat <ariya.hidayat@gmail.com>

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  */
function deduceSourceType(code) {
  try {
    esprima.parse(code, { sourceType: 'script' });
    return 'script';
  } catch (e) {
    return 'module';
  }
}

var mm = null;

function connect(fd, size) {
  mm = mmap(
    size,
    mmap.PROT_READ | mmap.PROT_WRITE, 
    mmap.MAP_SHARED, 
    fd, 
    0
  );
}

function tokenize(sz) {
  var source = mm.toString('utf8', 0, sz-1)
  
  source = removeShebangLine(source);
  /* TODO: retry on illegal tokens. */

  const sourceType = deduceSourceType(source);
  const tokens = esprima.tokenize(source, {
    sourceType,
    loc: true,
    tolerant: true
  });
  var s = JSON.stringify(tokens);
  var u = Buffer.from(s);
//   console.error(s.length);
//   console.error(u.length);
//   console.error(mm.length);
//   console.error(mm.constructor.name);
  u.copy(mm);
  
  return u.length;
}
function checkSyntax(sz) {
  var source = mm.toString('utf8', 0, sz-1)
  source = removeShebangLine(source);
  const sourceType = deduceSourceType(source);

  try {
    esprima.parse(source, { sourceType });
    return [];
  } catch (e) {
    return e;
  }
}

module.exports.tokenize = tokenize;
module.exports.checkSyntax = checkSyntax;
module.exports.connect = connect;