# Sutram R75 WS3 — smallest separate compilation limit

`ROADMAP-TO-V1.0.md` now explicitly places **separate compilation in v2**, not on the v1.0 critical path. WS2 kosh safety is prioritized in this round.

Current `yoj` is source/textual inclusion. There is no accepted compiler command that emits a relocatable native object from an individual `.sm` source and resolves a second compiled object's symbols. Thus compiling two actual Sutram modules independently and linking them cannot be truthfully claimed.

Smallest requested testcase:
`a.sm` declares `prakriya yog(a,b) { prati a+b }`.
`main.sm` declares `mukhya() { likha(yog(2,3)) }`.
Needed: compile a.sm to real native object, main.sm independently to object carrying an unresolved external symbol for yog, then resolve at link. A textual `yoj` would not satisfy this. Object output switch is not currently documented, and no attempt to run a nonexistent `--emit-obj` flag is described as a PASS or genuine test failure.

**NOT_RUN:** actual object output, external link, exported/private resolution, executable run, all acceptance. Do not reshape the NASM compiler for v2 while v1 memory safety is unresolved.
