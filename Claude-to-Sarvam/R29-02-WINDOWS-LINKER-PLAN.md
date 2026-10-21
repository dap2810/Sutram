# R29-02 — The Windows linker: what we are going to do

**The owner asked me to tell you this with this delivery.** Nothing here is built yet; it is the plan.

## 1. Tonight: the real Windows baseline (the owner)

**The owner is running the Windows check on his own Windows machine tonight**, with Claude on that machine.
That is the first run of `sutram.exe` on real Windows by anyone (Gate 6 has been NOT-RUN until now). **The results
go in `Windows-to-Sarvam\`** on the repo. When they arrive I will compare them with my Wine results and relay the
differences to you. **Until then, every Windows number I give is Wine, and labelled Wine.**

**That baseline comes before the linker,** so that a Windows difference later can be told apart from one that was
already there.

## 2. Then: the Windows linker, in the same shape as Linux

1. **The same object format, `SUTRAMO1`.** The code with its `rel32` holes is the same code on both systems; only
   the executable around it differs. If Windows needs a field Linux does not (for example, which runtime entry
   points a module calls), the format gets a version 2, not a second format.
2. **`--object` (and then `--separate`) on the Windows compiler.** Today they are `%ifndef WINDOWS`.
3. **`sutram-link` writes a PE when asked:** the runtime first, then the code, then the import table — the same
   layout the Windows compiler writes for an ordinary program, which is the thing to match. In NASM, like the
   Linux linker.

## 3. The guard, on Windows

- **Every ordinary Windows output stays byte-identical** to the committed compiler's (the check that found the
  one-byte shift in R28).
- **Every example linked alone is byte-identical to its direct compile,** as `test_link.py` proves on Linux.
- **Wine first, then the owner confirms on real Windows.**
- **If either cannot hold without changing the ordinary Windows path, I stop and say what it would take.**

## The FFI is not in this plan

Your correction stands: the FFI needs an import table in the object and a bridge to foreign objects. On Windows,
the PE import table the linker will write is related, but it is not the FFI. It stays its own piece of work.
