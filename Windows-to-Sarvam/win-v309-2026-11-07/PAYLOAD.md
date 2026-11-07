# v309 payload comparison (Task C)

**FAIL: two of the three checkout files differ from the package manifest solely because of CRLF.** The root `.gitattributes` at the tested commit still has no `*.md text eol=lf` rule. No attributes, source or package bytes were changed in this verification.

Tested commit: `7c92bc02ff6f81b4903a20c14712ad3fd566b0c4`. Obtained the checked-in release package from this Windows checkout; this is **not a newly built Windows package**. All **657/657 embedded payload entries** match their manifest. Package integrity and deterministic bytes across checkouts are different checks.

| File | Checkout SHA-256 | Manifest / embedded SHA-256 | Match? | Checkout CRLF? |
| --- | --- | --- | --- | --- |
| `docs/LANGUAGE-REFERENCE.md` | `cf7b12be17408c17b4f21200a6dcf8f27486dd9c957a9b1650e00a8704b227d1` | `0ea21b639c17be6956fbb02e516eccaf8235dc6cfd0b1cef5354af170650a830` | NO | True |
| `lang/sanskrit.lang` | `0b1940860bbfd54c1a5ee65f45bf31ffd1d4e68a0d95c5b5106ef1abdc1d0d9f` | `0b1940860bbfd54c1a5ee65f45bf31ffd1d4e68a0d95c5b5106ef1abdc1d0d9f` | YES | False |
| `README.md` | `9e08391ad8f82317de1a366da727a73e2e0f49f28b91029e71168b307168e8de` | `ab0ea01b9e8e13a95e1be50d36779f2153726308e7eaf7b4afecb45e1e34b9bd` | NO | True |

Both Markdown files become byte-identical to the embedded copies when CRLF is replaced with LF. All three embedded copies have no CRLF; the language pack already matches.

The requested PowerShell CRLF check on `docs/LANGUAGE-REFERENCE.md` returns **True**. [Native certutil and PowerShell output](payload-native-commands.txt), [comparison and attributes snapshot](payload.json), [all embedded hash checks](payload-all.json), [manifest](payload.manifest.sha256).

Sarvam should complete/review the root Markdown LF rule and deterministic packaging, then verify a fresh Windows checkout and compare actual Windows/Linux package manifests. This round does not establish a causal relationship between byte differences and any security-product action.
