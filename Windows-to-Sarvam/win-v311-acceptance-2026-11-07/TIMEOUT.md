# C: no installation stalled

The first installation reached Finish in **27.171 s** and reinstall in **40.188 s**. Both engines exited 0. No deliberate stall, process suspension, security-policy change or timeout injection was performed.

Therefore the 15-minute timeout was **not exercised** in this round, as allowed by [the brief](REQUEST.md). Do not infer that its expiration, log, or UI outcome has been verified. The observer allowed 970 seconds, longer than the native 900-second deadline; neither run approached that limit or needed cleanup termination (`stopped_in_cleanup` is empty in both records).

[First install record](first-install.json), [first log](first-install-engine.log), [reinstall record](reinstall.json), [reinstall log](reinstall-engine.log). Wizard closure occurred after clicking Finish in each run. Prior externally suspended runs remain separate historical evidence.
