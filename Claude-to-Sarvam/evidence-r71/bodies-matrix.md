| construct (indented body) | expected | v264 | v265 | v266 | v267 |
|---|---|---|---|---|---|
| yadi, body of 3 | 3 | 3 | 3 | 3 | 3 |
| yadi false, body of 3 skipped | 0 | **2** | 0 | 0 | 0 |
| yadi / anya, 3 in each | 3 | **REFUSED: Sutram Error: vyakaran dosh, pankti 8:11, shabd '='** | 3 | 3 | 3 |
| yadi / anya yadi / anya | 3 | **REFUSED: Sutram Error: vyakaran dosh, pankti 8:9, shabd 'c'** | 3 | 3 | 3 |
| yavat, body of 3 | 6 | **HANGS** | 6 | 6 | 6 |
| chakra i = a tak b | 9 | **5** | 9 | 9 | 9 |
| chakra i = a arabhya b paryantam | 9 | **5** | 9 | 9 | 9 |
| kuru ... yavat (c) | 6 | **REFUSED: Sutram Error: vyakaran dosh, pankti 6:9, shabd 'c'** | 6 | 6 | 6 |
| guna without braces (guna requires { } - refused loudly, not silently) | REFUSED | REFUSED: Sutram Error: vyakaran dosh, pankti 5:9, shabd 'bhavana' | REFUSED: Sutram Error: vyakaran dosh, pankti 5:9, shabd 'bhavana' | REFUSED: Sutram Error: vyakaran dosh, pankti 5:9, shabd 'bhavana' | REFUSED: Sutram Error: vyakaran dosh, pankti 5:9, shabd 'bhavana' |
| guna { } with indented bhavana bodies | 3 | **REFUSED: Sutram Error: vyakaran dosh, pankti 7:13, shabd 'c'** | 3 | 3 | 3 |
| yadi dosh (q = call) / anya | 3 | **REFUSED: Sutram Error: vyakaran dosh, pankti 14:11, shabd '='** | 3 | 3 | 3 |
| mukhya without braces runs to end of file: a prakriya after it is inside it (compiled, callable) | 1 | 1 | 1 | 1 | 1 |
| mukhya with braces, then a statement after it (silently dropped before v266) | REFUSED | **1** | **1** | REFUSED: Sutram Error: vyakaran dosh, pankti 4:1, shabd 'likha' | REFUSED: Sutram Error: vyakaran dosh, pankti 4:1, shabd 'likha' |
| prakriya without braces, then mukhya | 4 | **REFUSED: Sutram Error: vyakaran dosh, pankti 3:5, shabd 'b'** | 4 | 4 | 4 |
| two prakriya without braces | 12 | **REFUSED: Sutram Error: vyakaran dosh, pankti 3:5, shabd 'nivartanam'** | 12 | 12 | 12 |
| mukhya without braces, 3 statements | 3 | 3 | 3 | 3 | 3 |
| nested: yavat > yadi > yavat | 22 | **HANGS** | 22 | 22 | 22 |
| indented body containing a braced block | 22 | **HANGS** | 22 | 22 | 22 |
| braced body containing an indented block | 22 | **23** | 22 | 22 | 22 |
| one-statement body on the next line, same indentation (unchanged rule) | 1 | 1 | 1 | 1 | 1 |
| body on the header's line (unchanged rule) | 1 | 1 | 1 | 1 | 1 |
| statement continued over two lines inside a body | 6 | 6 | 6 | 6 | 6 |
| two statements on a one-statement body's line (the second ran outside before v267) | REFUSED | **10** | **10** | **10** | REFUSED: Sutram Error: vyakaran dosh, pankti 3:30, shabd 'c' |
| two statements on one line inside an indented body (both in the body) | 0 | **10** | 0 | 0 | 0 |
| tab-indented body | 2 | 2 | 2 | 2 | 2 |

v264: 8/25 as written
v265: 23/25 as written
v266: 24/25 as written
v267: 25/25 as written
