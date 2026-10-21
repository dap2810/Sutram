# R25-03 — WS3: the type-on-variables decision, for the owner

**Not built. This is the decision, in one paragraph.**

Today a Sutram variable has no type: a parameter is one qword, so the compiler cannot tell a list from a
number. Giving **parameters** a declared kind — `mala`, `kosh`, `vibhag`, a `rachana` name, or a function
— and letting each local take the kind of whatever it is declared from (which the compiler already tracks
for `mala`, `kosh`, slices and `dasham`), **unblocks four things at once:**

1. **F7:** passing a number where a list is indexed becomes a compile error instead of a crash.
2. **Checked calls through function values:** a call through a value gets its number of arguments and
   whether it is a function checked.
3. **Method dispatch on the object's type:** `p.chal()` calls the method of `p`'s own `rachana`, so two
   `rachana`s can each have a `chal`.
4. **Traits:** a set of methods that several `rachana`s can each provide.

**What it costs.** In the **required** form, the compiler would refuse an untyped parameter that is
indexed, has a field taken, or is passed to a typed one. ROUND-19 measured **371 one-word annotations:**
236 library functions and 135 functions in programs. Without them, 32 program files and all of `lib/`
stop compiling. ROUND-20 measured the narrowest required form, which covers indexing only and so only
item 1 of the four: 116 annotations, with 15 of 24 modules and 185 programs stopping without them. In
both forms **no call site changes and no program's output changes,** because the annotation is on the
declaration and the check is at compile time. The **optional** form costs nothing and closes nothing until
the annotations are written.

**What I would choose: the required form, staged over two rounds.** Round 1 adds the kinds as an
optional feature and writes all 371 annotations in the library and the programs. That is mechanical work,
and the suite proves it changes no output. Round 2 makes the kinds required and builds items 2–4 on them.
The reason is that the optional form alone never closes F7 or delivers items 2–4. A required form landed
all at once is a flag day for every program at the same moment. Staging gives the safety of the first with
the result of the second.

**What I need from the owner:** yes or no to **required**, and whether the parameter kind is written as a
word before the name, `prakriya f(mala a, Bindu p)`. That fits the existing `dasham a` and `kosh a`, and it
is what I would use.
