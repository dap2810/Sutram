# Exact v311 candidate

Source checkout: `2e8f2ea4085925f862450b16d444313eefdbb007`. The setup is the unchanged upstream v311 artifact.

```text
Sutram 1.0 (v311) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

| Artifact | SHA-256 |
| --- | --- |
| Setup / installed uninstaller | `134fae95dc9d79a0cc7e563bbf59e6fc69983eae950c2c2799e20dea911a286b` |
| Compiler (repository, embedded and installed) | `9740b045ef19ebcf0300010724803d61ecd8e4d3a1e0e23523b558d1dac974fb` |
| Embedded install-core.ps1 | `b08e8fcd14611f8e80385b4fc26b43189918a760a4318d2ca6da3083175f1820` |
| Payload manifest | `710e90b5fdd9bbac9655e45e45935a442902209062eb82a90da44f41e217300d` |

[candidate.json](candidate.json) records the embedded 657 files and verifies that the source engine bytes are present in the setup. [final-identity.json](final-identity.json) verifies 657/657 installed hashes, the exact manifest/uninstaller, registry version 1.0.311, one canonical compiler in a fresh registry-PATH shell, and no pending manifest/transaction.
