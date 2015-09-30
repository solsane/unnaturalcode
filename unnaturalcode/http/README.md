# HTTP API for [UnnaturalCode][]

# Run

    python -m unnaturalcode.http

See the repository root for running all tests. 

# All rooted on resource `/{corpus}`

 * Currently, only the `py` and `generic` corpora are supported.

# Corpus info—`GET /{corpus}/`

Returns metadata for the given corpus. Metadata includes:

 * `name`
 * `description`
 * `language`—programming or otherwise
 * `order`— order of the *n*-gram
 * `smoothing`—Probably always `ModKN` ([Modified Kneser-Ney][ModKN])

[ModKN]: http://en.wikipedia.org/wiki/N-gram#Smoothing_techniques


# Predict—`GET /{corpus}/predict/{prefix*}`

     GET /py/predict/<unk>/for/i/in HTTP/1.1

     {"suggestions": [3.45, ["range", "(", "5", ")", ":"]]}

## Mandatory arguments

The prefix must be given in the path.

### `{context*}`

Preceding token context. The more tokens provided, the better, but
you'll probably want to have at least three in most cases.



# Predict—`POST /{corpus}/predict/`

     POST /py/predict/ HTTP/1.1
     Content-Type: multipart/form-data; ...

     [...file upload...]

     {"suggestions": [3.45, ["range", "(", "5", ")", ":"]]}

## Mandatory arguments

Use one of `?f` or `?s`:

### `?f`

Upload a file in a multipart message as `?f`. The file will
automatically be tokenized if the corpus is the Python corpus.
When using the generic corpus, a JSON format is expected. The
JSON format looks like:

    [   
        {   
            "end": [ 1, 5 ],
            "start": [ 1, 0 ],
            "type": "FUNCTION",
            "value": "print"
        },
        {   
            "end": [ 1, 21 ],
            "start": [ 1, 6 ],
            "type": "STRING",
            "value": "\"Hello, World!\""
        },
        {   
            "end": [ 1, 23 ],
            "start": [ 1, 22 ],
            "type": "NEWLINE",
            "value": "\n"
        }
    ]
Where `end` is the ending line and column of the token, `start` is the starting
line and column of the token, `type` is the token's type, and `value` is the
token's literal text.


### `?s`

Post a string excerpt `?s`. The file will automatically be tokenized, or
if the generic corpus is used, it should be provided in the JSON format
described above.



# Cross Entropy—`POST /{corpus}/xentropy`

Compute the cross entropy of a file with respect to the corpus. Gives
a number from 0 to ∞ that indicates how surprised the language model is
by this file.

## Mandatory arguments

Use one of `?f` or `?s`:

### `?f`

Upload a file in a multipart message as `?f`. The file will automatically be tokenized, or
if the generic corpus is used, it should be provided in the JSON format
described above.

### `?s`

Post a string excerpt `?s`. The file will automatically be tokenized, or
if the generic corpus is used, it should be provided in the JSON format
described above.



# Train—`POST /{corpus}/`

Trains the corpus with a file. The file will automatically be tokenized, or
if the generic corpus is used, it should be provided in the JSON format
described above.

## Mandatory arguments

Use one of `?f` or `?s`:

### `?f`

Upload a file in a multipart message as `?f`. The file will
automatically be tokenized.

### `?s`

Post a string excerpt `?s`. The file will automatically be tokenized.



# Licensing

Like [UnnaturalCode][], UnnaturalCode-HTTP is licensed under the AGPL3+.

© 2014 Eddie Antonio Santos

UnnaturalCode-HTTP is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

UnnaturalCode-HTTP is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with UnnaturalCode-HTTP. If not, see http://www.gnu.org/licenses/.

[UnnaturalCode]: https://github.com/orezpraw/unnaturalcode
