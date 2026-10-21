# R25-01 — WS1: the four files restored, and how to merge a file that is not text

## Restored

`tests/negative/r17/r15-original/mutation-15-{27971,37233,42057,574}.sm` on main are the fuzzer's bytes
again. I took them from `e2cdbe92` (my ROUND-20 commit, which wrote them byte-exact) and pushed them with
git. `SHA256SUMS` is unchanged, as it was right:

```
7d42c065f75f419e1c75396f8e8d7b3215ca9d9899f5253be38ca008f7b00907  mutation-15-27971.sm
768e294160e48a93842dc9e5cc1eaafa7a30d29fc4ea256a92e248d9dfadc8a7  mutation-15-37233.sm
b251932b7364045da371e112ce1fe8efc1b9b160d074e7394f68e45d9ddb536d  mutation-15-42057.sm
2abae6b7323622ef12e4064ca90aaaa9ed79cca6fd3887b6135c985827b50bc7  mutation-15-574.sm
```

**To check them yourself** (this reads the bytes and writes nothing):
`cd tests/negative/r17 && sha256sum -c SHA256SUMS` → 213 × `OK`.

The git blobs are in `FILES-R25.txt`: `a6c1747d`, `715b9a7c`, `a255cd01`, `ac9dbf77`.

**`crash corpus: 227 cases + manifest, 0 failed`** (Linux). On v226's compiler the four crash again, as
they did when the fuzzer found them.

## Your question: how do I merge a file that is not valid UTF-8?

**Plainly: you cannot, with a tool that reads files as text and writes text.** Decoding with
`errors="replace"` destroys the bytes at the read, before anything is written. No setting on the write
side can bring them back. **Use a git operation instead.** In order of preference:

1. **GitHub's Merge button on the PR, or `git merge` / `git cherry-pick` on a clone.** Git copies blobs and
   never decodes them. This also carries file modes, which a text write cannot set either.
2. **If your tool can call the GitHub API with raw bytes:** the Contents API (`PUT
   /repos/{owner}/{repo}/contents/{path}`) takes the content **base64-encoded**. The base64 must be made
   from the file's **bytes**, read in binary (`open(p, 'rb')`), never from decoded text. The same limit
   applies: if the bytes passed through a UTF-8 decode first, they are already gone.
3. **Avoid the problem:** store such files as text. R24 did this for these four (`NAME.sm.b64`, decoded by
   the runner), and a text copy cannot damage those. I did not apply it this round, because you asked for
   the `.sm` files back. It is one commit if you want it.

**A guard for your tool, which would have stopped all three corruptions:** before writing any file, decode
it strictly (`data.decode('utf-8')` with **no** `errors=`). If that raises, stop and hand the file to a git
operation. The same test catches the executables: their mode is not content, so they always need git.
