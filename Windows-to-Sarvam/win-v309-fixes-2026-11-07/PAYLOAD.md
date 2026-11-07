# Payload determinism fixed

Native Windows PowerShell built the candidate; native Ubuntu/WSL Python built the Linux payload from the same product source `4536cc36a083a64a0382cfff14a78a298a5bae1b`. All **657 payload entries and the manifest** match byte for byte. [Complete comparison](payload-comparison.json).

| Fresh checkout sample | Windows checkout = Linux checkout = payload SHA-256 | Result | Windows CRLF? |
| --- | --- | --- | --- |
| `README.md` | `ab0ea01b9e8e13a95e1be50d36779f2153726308e7eaf7b4afecb45e1e34b9bd` | MATCH | False |
| `docs/LANGUAGE-REFERENCE.md` | `0ea21b639c17be6956fbb02e516eccaf8235dc6cfd0b1cef5354af170650a830` | MATCH | False |
| `lang/sanskrit.lang` | `0b1940860bbfd54c1a5ee65f45bf31ffd1d4e68a0d95c5b5106ef1abdc1d0d9f` | MATCH | False |

The fresh Windows sample checkout is `build/windows-v309-fixes-fresh` at `8321f843` (the LF rule commit); the later product commits alter manifest ordering/linker lookup and INSTALLER-REBUILD.md, not these samples. The Linux payload and native Windows package use final product source `4536cc36`. The original Windows worktree still contained CRLF in the two Markdown samples; its package nevertheless matches because normalization occurs in staging. The checkout is not rewritten by packaging.

Manifest SHA-256: `0523ff8050787c529777727998aaffd3d1c144e2fd8ed31100c0e220b559d096`. Compiler, linker, GUI and icon payloads remain byte-identical to the original inputs. Invalid UTF-8 in a declared text file is refused; binaries are not decoded or normalized.

The first comparison established equal file contents but found different manifest ordering around underscores. It is retained in [the initial comparison](payload-comparison-before-order-fix.json). Both builders now sort ordinal UTF-16 paths and use identical CRLF manifest separators. The final comparison passed after rebuilding both.

`payload-native-commands.txt` records the **old/stale worktree's** certutil/CRLF checks, so its True result is expected. The fresh-checkout samples above are the evidence for the attribute fix. Complete ZIP/setup bytes are not claimed reproducible: metadata/compression/linkers differ. No security-product causal claim follows from equal file hashes.
