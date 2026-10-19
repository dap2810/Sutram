# Sutram — security and least-privilege audit

**Step 8 of `ROADMAP-TO-V1.0.md`.** Measured 2026-10-19 at v189.
**Method:** scanned the shipped code for network calls, elevation requests, registry writes and credentials;
every finding below is a file and a line, not an impression.

**The constraints being audited** (set by the owner at the start): per-user install only, no administrator
rights, no UAC prompt, nothing written outside the user's own account, no credentials, no new network access.

---

## Verdict

| Constraint | Status | Evidence |
|---|---|---|
| Per-user install, no admin | **HONOURED** | the native installer writes **HKCU**; the preflight **forbids** elevation |
| No elevation request | **HONOURED** | `preflight-windows.ps1` rejects `-Verb RunAs`, `RelaunchElevated`, `ExecutionPolicy Bypass` |
| No credentials | **HONOURED** | no key, secret, token or password anywhere in the shipped code |
| No network access | **BY DESIGN, NOT BY ACCIDENT** | the language ships `net*` builtins — see below |
| Nothing outside the user account | **ONE EXCEPTION** | `windows/sutram-installer.nsi` writes **HKLM** — see below |

---

## 1. The one real violation — `windows/sutram-installer.nsi` writes HKLM

```
windows/sutram-installer.nsi:63:  WriteRegStr HKLM "Software\${APPNAME}" "InstallDir" "$INSTDIR"
windows/sutram-installer.nsi:65:  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\..." ...
```

**Six writes to `HKLM` — the machine-wide registry — including the uninstall entry.** Writing HKLM requires
administrator rights, which is precisely what the owner ruled out.

**It is superseded.** The shipped installer is the native one (`windows/native-installer/`), which is
per-user. But the `.nsi` file is **still in the tree and still referenced** by `windows/WINDOWS-README.md`
and `windows/windows-build-integrity.sha256`.

**Recommendation: retire it.** Delete the file and remove it from the two references. It is dead code that
describes an installer nobody ships, and its presence means a reader — or a future build — can pick up a
machine-wide installer by mistake. **This is the same finding I raised in an earlier audit and did not act
on; it should not survive another.**

## 2. Good news — the preflight is a guard, not a violation

My first scan flagged `RunAs` in `windows/preflight-windows.ps1`. **It is the opposite of a violation:**

```powershell
foreach ($bad in @('ExecutionPolicy Bypass','HKLM:', '::LocalMachine','MachinePathEntry','-Verb RunAs','RelaunchElevated')) {
    if ($text.IndexOf($bad, ...) -ge 0) { throw "Forbidden active build/install behavior in ${rel}: $bad" }
}
```

**It actively refuses to build an installer that elevates, writes machine-wide, or bypasses execution
policy.** That is a least-privilege guard implemented as a build check — **the constraint is enforced by
code rather than promised in a document.** Worth keeping and worth pointing at.

## 3. The language ships networking builtins — a decision, not a defect

`src/sutram_compiler.asm` contains `socket`, `bind`, `listen` and `accept` — the `net*` builtins
(`netsock`/`netbind`/`netlisten`/`netaccept`).

**This is not a violation of the constraints** — the constraints are about the *installer*, not the language.
But it is worth stating plainly, because it has two consequences:

1. **A language for beginners that can open a listening socket is a security surface.** A user can write a
   program that listens on a port. That is normal for a systems language and surprising for one aimed at
   first-time programmers.
2. **It has never been exercised.** The layer check treats `netsock`/`netbind`/`netlisten`/`netaccept` as
   `std`-layer calls and forbids `core` modules from using them — so the boundary is specified — **but no
   test in the tree opens a socket.**

**Recommendation: keep them, document them, and say in `PROJECT-MASTER.md` §9 that the language can open
sockets.** A learner should not discover that by accident.

## 4. Checked and clean

- **No credentials** — no `api_key`, `secret`, `password`, `token` or `bearer` anywhere in shipped code. *(The
  word `token` appears in the Linux GUI; it is a **lexer token**, not a credential.)*
- **No HTTP client** — no `winhttp`, `wininet`, `InternetOpen`, `curl` or `ws2_32` in the compiler, the IDE
  or the installer.
- **The native installer is per-user** — HKCU, seven writes, no machine-wide state.

---

## What still cannot be verified from here

**The installer's behaviour on a real Windows machine.** This audit is a **static scan of the source** — it
shows what the code *says* it does. It does not show what the built binary does. **The owner's own install is
the only check of that**, which is why the acceptance is his.

**And this audit does not cover the compiler's generated code.** It covers the shipped tooling. A program a
user writes can do anything the language allows — including the sockets above.
