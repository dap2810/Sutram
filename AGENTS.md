# Sutram contributor/agent instructions

## Read this first

**`PROJECT-MASTER.md`** is the single patra to read before touching anything: what Sutram is, the
main goal, the philosophy, the nine paradigms, the twenty design parameters with honest status,
the history, how the project is built, the hard constraints, what is *not* true yet, and how to
work on it.

Then read **`docs/sutram-design-parameters.html`** — the design charter.

**Docs are part of the change, not a task after it.** A round that changes behaviour updates the reference
(`docs/LANGUAGE-REFERENCE.md`), the changelog (`docs/CHANGELOG.md`) and any book chapter that describes that behaviour
(`docs/sutram-book-english.html`, `docs/sutram-book-sanskrit.html`), in the same commit. The gate `R158 doc currency`
checks it; do not rely on the gate to remember what you forgot - it catches a missing version number, a symbol that
does not exist, a book example that does not run, a flag the compiler refuses; it does not catch a paragraph that is
now false. (The owner's standing instruction: *"The docs should be up to date as we progress."* R158.)

**Never write the owner's system details into this repository (the owner's standing instruction, 9 November 2026).**
The repository is public. In every file - reports, evidence, JSON, logs, transcripts, commit messages, code comments -
write no home folder (`C:\Users\<anything>`, `/home/<anything>`), no user or computer name, no drive letter or
absolute path outside the repository, no OS build number, no hardware detail, no IP or MAC address, no screenshot
file name that encodes a path. Write `%USERPROFILE%`, `<repo>`, `%TEMP%`, `<scratch>` and "Windows 11" instead: a
path is evidence, a user name is not. The gate `R159 no personal paths` (`tests/r159/test_no_personal_paths.py`)
fails on any of them in a tracked file; `tools/normalize_personal_paths.py` replaces them keeping what each line
says. It cannot clean the history (`git log -p`) or read text inside an image. **The owner had every screenshot of
a machine removed from the tree (9 November 2026; list in `Claude-to-Sarvam/evidence-r164/screenshots-removed.tsv`).**
A screenshot shows what a text gate cannot see - the installer's *Ready* page prints the profile folder, a prompt
prints it too. Report what a screen showed in words; if a picture is indispensable, cover the details first
(`tools/redact_screenshots.py`), look at it yourself, and say so.

**Evidence stays, and so does the history (decided by Sarvam, R161).** The repository is large because every claim
in it is backed by evidence - most of it from running each candidate on a second platform. A file a report names, a
script made, or a wildcard in a report covers is part of the record: if the record says "the guard showed 587
identical" and the guard's output is gone, the record is a claim without evidence. **Cited evidence is not deleted.**
A file that is a byte-identical copy of one that stays may go, with a manifest of what went and where the kept copy
is. **History is not rewritten.** Rewriting it would shrink the clone (most of the history is old binaries), but it
would change every commit SHA - which hundreds of round records and the guard's baselines cite - force every clone,
the owner's Windows clone among them, to be made again, and need a forced push. We keep the evidence and accept the
size. If a small download is wanted for a release, make a new repository from the release tree and keep this one as
the archive. Do not reopen this without the owner.


These instructions apply to every automated coding assistant working in this repository, including ChatGPT, Sarvam and additional collaborators.

## Mandatory GitHub Actions notification safeguard

- **No experimental workflow runs automatically on every commit.** New workflow files must use `workflow_dispatch` only (or `workflow_call` for an explicitly invoked reusable workflow). Do not use `push`, `pull_request`, `schedule` or other automatic triggers without prior explicit repository-owner approval.
- Before changing `.github/workflows/*`, run `python3 tools/check_workflow_triggers.py` and `python3 -m unittest discover -s tests/ci -p 'test_*.py' -v` against the target branch. If the checker fails, fix triggers BEFORE pushing; do not turn the checker into an automatically triggered workflow.
- Do not launch a full CI run after each small fix or documentation change. Wait until a substantial reviewed/testable milestone and deliberately trigger one run. Investigate observed failures before retrying.
- Changing workflow trigger YAML does not suppress already-sent GitHub notification emails. See `docs/CI-NOTIFICATION-POLICY.md`.

## Sutram handoff and source discipline

- Only check `Sarvam-to-ChatGPT/` when the user requests a folder check or starts work. Do not sangrah up background watching without explicit instruction.
- Preserve the pure NASM compiler, native outputs, existing frozen baselines and agreed regression gates. Test what you claim, report failures and timing variance.
- Keep unapproved code changes in review branches/draft PRs. Put instructions and verified logs in `ChatGPT-to-Sarvam/` on `main` as documentation-only commits, pending Sarvam's independent acceptance.
- On Windows testing, do not claim that the IDE, installer, shell or canonical icon is accepted based on PE-structure validation alone. Use real native execution and screenshots where available.
