# Installation state before and after: partial, unchanged

Both diagnostic attempts left all 137 existing files byte-identical, with
unchanged user/machine PATH and unchanged (absent) HKCU uninstall registration.
See [before](before.json), [after](after.json), and
[scope comparisons](path-scopes.json). The first and second before-snapshots
also match. The failed engines left their diagnostic TEMP staging folders;
these were not removed by us.

Reconstructed persisted PATH, queried in a new child process, resolves:

```text
%USERPROFILE%\AppData\Local\Programs\Sutram\bin\sutram.exe
```

`sutram --version`, both before and after:

```text
Sutram 1.0 (v305) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

This was already v305 at the start of this round. It must not be described as
v303 based on an earlier snapshot, nor as a compiler newly installed by these
failed attempts. Installed compiler: 530,040 bytes, SHA-256
`4c05d5cbad99b32be1a38459f1b4b794e00f8b34f89a662ef1ca363c92ec1603`.
Current package/compiler SHA-256:
`db5eda53871aafa4749d593ddef2d29e2841e3eb4d3cb7cdf680223fb45a073c`.
Matching version text does not make these binaries identical.

`%LOCALAPPDATA%\Programs\Sutram` contains:

```text
assets/
bin/
docs/
.sutram-install              29 bytes
install-state.ini           828 bytes
install.log                 756 bytes
payload.manifest.sha256   62225 bytes
Sutram-Uninstall.exe    1946102 bytes
```

Its `bin/` contains `lang/`, `lib/`, `sutram-link.exe` (19,870 bytes), and
`sutram.exe` (530,040 bytes). The uninstaller exists as `Sutram-Uninstall.exe`;
the handoff's literal `uninstall*` glob would miss that filename, so the snapshot
records `*uninstall*`. Its presence does not establish a complete installation.

The installation lacks the root GUI executable, `win/`, and `examples/` among
many other package files. Against the **current package's 657 manifest entries**:

- 122 present files match their package hash.
- 525 entries are missing.
- 10 present files have different hashes, including the compiler.

All missing/mismatching paths are in [payload-audit.json](payload-audit.json).
The old installed manifest has 643 entries; 512 of those are missing too. The
installer's ownership refusal compares against that old manifest, not the
current package's content. The existing linker matches the current package but
differs from the old ownership hash, so retry refuses before it can repair the
partial layout.

**Answer to Task B:** the available state is a partial copy, not merely a missing
final step after a complete copy. A runnable `bin\sutram.exe` alone cannot
distinguish those conditions. These two attempts themselves copied no installed
payload files; the partial state was already present.
