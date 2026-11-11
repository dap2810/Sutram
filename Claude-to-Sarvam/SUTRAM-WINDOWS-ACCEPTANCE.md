# Sutram on Windows — the acceptance run

**What this is.** Eleven versions of the Sutram compiler (v316 to v326) are built and tested on Linux, and none can
be released until one person runs them on a real Windows machine. This page is that run, step by step. **You do
not need to know anything about Sutram.** Each step says what to type, what you should see, and what it means if
you see something else.

**What you need:** a Windows 10 or 11 computer, an ordinary user account (**not** an administrator - the
installer must not need one), an internet connection, and about 30 minutes.

**What you send back:** section 10, filled in. **Write what the screen showed, not what you expected.** Do not
send screenshots, and do not copy any line that shows your user name or a folder under `C:\Users\` - write
`%USERPROFILE%` in its place. The repository is public.

**The artifact this run tests** - everything below is pinned to it:

| | |
|---|---|
| the installer | `Sutram-Setup.exe` |
| its SHA-256 | `160a1ab6f38b5263aabfd625aad3e624f705d9fd2d524c05644c197b7405f4fc` |
| from the repository's commit | `c3b7b9ef185cfbe7e5a65d205f36a85bb195e168` on branch `r190-chakra-and-converter` |
| the compiler inside it | `Sutram 1.0 (v326) - sampurna sutra` |
| the compiler file's SHA-256 | `F22FEA3FEEFB0547816494EE53C4F6DB878FB471C563E4776D0AA029FF252304` |

**Why v326:** it is the top of the chain, so it contains all eleven versions; one run here covers them all. **This
page was first issued for v324 (installer `c82bbca5...`), reissued for v325 (`9af56fad...`), and is reissued for
v326.** v326 adds one compile-time warning and one library function to v325; every output below is the same as
v325's except the version line. If the run is wanted on an earlier version, say so and the page is reissued for
that installer.

**How to read the expected output.** A grey block is what the screen must show. **Every character matters** unless
the step says otherwise. Where a step cannot be checked from what is printed, it says so.

---

## 1. Download the installer and check it is the right file

Open **PowerShell** (Start menu, type `powershell`, press Enter - *not* "Run as administrator"). Then:

```powershell
cd $env:USERPROFILE\Downloads
Invoke-WebRequest -Uri https://github.com/dap2810/sutram/raw/c3b7b9ef185cfbe7e5a65d205f36a85bb195e168/Sutram-Setup.exe -OutFile Sutram-Setup.exe
(Get-FileHash .\Sutram-Setup.exe -Algorithm SHA256).Hash
```

**You should see exactly:**

```
160A1AB6F38B5263AABFD625AAD3E624F705D9FD2D524C05644C197B7405F4FC
```

| if you see | it means | fatal? |
|---|---|---|
| a different hash | this is not the tested file - a different download, or a changed one | **Yes. Stop.** Send the hash you got. |
| `Invoke-WebRequest : 404` | the commit is not published, or the link is mistyped | Stop; check the link, else send the message |

## 2. Run the installer

Double-click `Sutram-Setup.exe` in your Downloads folder.

**Before the wizard - possible, and not a failure:** Windows may show a blue box, *"Windows protected your PC"*.
That is SmartScreen: it warns about any program that is not signed and not yet widely downloaded, and this one is
neither. **The hash check in step 1 is what tells you the file is the right one.** Choosing *More info* -> *Run
anyway* is your decision to make; if you decline, the run ends here - record that.

| if you see | it means | fatal? |
|---|---|---|
| **"Do you want to allow this app to make changes to your device?"** (a User Account Control prompt) | the installer asked for administrator rights. It must not. | **Yes. Click No and stop.** Record it. |
| your antivirus blocks or quarantines the file | | **Yes. Stop.** Do not turn the antivirus off. Record its exact message. |

**The wizard, page by page.** Each page's title must be as written. Click the button named in the last column.

| page title | what the page says (in part) | what you do |
|---|---|---|
| **Welcome to Sutram Setup** | *This wizard will install Sutram, the Sanskrit-keyword programming language, on your computer.* and *Sutram installs for the current Windows user only. No administrator rights are needed, ...* | **Next >** |
| **License Agreement** | the licence text; two choices, and ***I do not accept*** **is selected when the page opens** - Next is not usable until you change it | select **I accept the terms of the license agreement**, then **Next >** |
| **Choose Install Location** | *Install location:* and a folder ending in **`\AppData\Local\Programs\Sutram`** | leave it as it is; **Next >** |
| **Select Components** | two boxes: **Add Sutram to my user PATH (recommended)** - **ticked**; **Create a desktop shortcut (Sutram IDE)** - **not ticked** | leave both as they are; **Next >** |
| **Ready to Install** | *Destination folder:* (the same folder), **`Add to user PATH: yes`**, **`Desktop shortcut: no`** | **Install** |
| **Installing Sutram** | *Extracting package files...*, then *Running setup script (this can take a minute)...*, then *Finalizing installation...* | wait - up to a few minutes |
| **Completing the Sutram Setup Wizard** | ***Sutram has been installed successfully.*** and *You will find Sutram IDE and Sutram Terminal in your Start Menu.*; a box **Launch Sutram IDE**, ticked | **untick Launch Sutram IDE**, then **Finish** |

| if you see | it means | fatal? |
|---|---|---|
| *"Sutram setup did not complete. Check the install log in %TEMP% ..."* | the install script failed | **Yes.** Open `%TEMP%`, find the newest folder whose name starts `STM`, and send the **last 20 lines** of `install.log` in it (replace your user name in any line with `%USERPROFILE%`). |
| *"Sutram is already installed at: ..."* or *"Another Sutram is already installed"* | an older Sutram is on this account | Not a defect. Uninstall the old one (Settings -> Apps -> Installed apps -> Sutram), then start step 2 again. Record that you did. |
| *"Sutram setup could not start Windows PowerShell."* | PowerShell is blocked on this machine (often an organisation policy) | **Yes, for this machine.** Record it; do not change the policy. |
| the location page shows a folder **not** under `AppData\Local\Programs` | the default is wrong | **Yes.** Record the folder (with `%USERPROFILE%`). |
| a page title or box differs from the table | the wizard is not the one tested | Not fatal; record exactly what it said, and go on. |

## 3. The installed compiler

**Open a new PowerShell window** (close the old one: a PATH change reaches only windows opened after it). Then:

```powershell
sutram --version
```

**You should see exactly these two lines:**

```
Sutram 1.0 (v326) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

```powershell
(Get-Command sutram).Source -replace [regex]::Escape($env:USERPROFILE), '%USERPROFILE%'
(Get-FileHash (Get-Command sutram).Source -Algorithm SHA256).Hash
```

**You should see:**

```
%USERPROFILE%\AppData\Local\Programs\Sutram\bin\sutram.exe
F22FEA3FEEFB0547816494EE53C4F6DB878FB471C563E4776D0AA029FF252304
```

| if you see | it means | fatal? |
|---|---|---|
| `sutram : The term 'sutram' is not recognized ...` | the PATH entry was not added, or this window was opened before the install | Open a **new** window and try again. Still there: **yes, fatal** - the PATH step failed. |
| a version other than `(v326)` | a different compiler answers - check the next line | **Yes.** |
| a path not ending `\AppData\Local\Programs\Sutram\bin\sutram.exe` | another `sutram.exe` comes first on your PATH | **Yes.** Record the path (with `%USERPROFILE%`). |
| a different hash | the installed compiler is not the tested one | **Yes.** |
| no output at all from `sutram --version`, or a Windows error box | the compiler does not start on this Windows | **Yes - the most important failure on this page.** Record the box's exact text. |

## 4. Write the three test programs

Paste this whole block into the same PowerShell window. It makes a folder `sutram-accept` in your temporary folder
and writes three small programs into it, byte for byte, then prints each file's hash.

```powershell
$d = Join-Path $env:TEMP 'sutram-accept'
New-Item -ItemType Directory -Force -Path $d | Out-Null
Set-Location $d
$n = [string][char]10
function Write-Sm($name, $lines) { [IO.File]::WriteAllText((Join-Path $d $name), (($lines -join $n) + $n)) }
Write-Sm 'accept.sm' @(
'mukhya() {',
'    likha("nama? ")',
'    vitti nama = vartani_grahan()',
'    vitti a = grahan()',
'    vitti yoga = 0',
'    chakra i = 1 tak 800000 {',
'        kosh k[4]',
'        kosh_kship(k, i)',
'        yoga = yoga + kosh_gan(k)',
'    }',
'    mandapa {',
'        vitti p = nirmmita(1000000)',
'        p[0] = 7',
'        yoga = yoga + p[0]',
'    }',
'    likha("Namaste, ", nama, "!\n")',
'    likha("sankhya: ", a, "  yoga: ", yoga, "\n")',
'    likha("smriti: ", parimana(), "\n")',
'}'
)
Write-Sm 'smriti.sm' @(
'mukhya() {',
'    vitti yoga = 0',
'    chakra i = 1 tak 800000 {',
'        kosh k[4]',
'        kosh_kship(k, i)',
'        yoga = yoga + kosh_gan(k)',
'    }',
'    likha("yoga: ", yoga, "\n")',
'    likha("smriti: ", parimana(), "\n")',
'}'
)
Write-Sm 'curly.sm' @(
'mukhya() {',
('    likha(' + [char]0x201C + 'namaste' + [char]0x201D + ')'),
'}'
)
Get-ChildItem *.sm | Sort-Object Name | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash + '  ' + $_.Name }
```

**You should see exactly:**

```
E51115D9BB0477201FC36711280588857AAA81472A4B5C93EDE1B8DA9B8ABC39  accept.sm
B0A7F67D0D872D6CEF36F840B5E0D485A39D4CF52A4EE3211D05AD6F94B39C30  curly.sm
CE53988FD35E8C511D604206F288FB5B9D1EBF9EA93AA485A92E0D87E131F7C4  smriti.sm
```

**A different hash is not a Sutram failure** - the paste changed a character. Paste the block again. If it still
differs, record the hashes and stop at this step: steps 5 to 7 would test a different program.

## 5. One program that uses what changed

`accept.sm` asks for a name and reads it as text (`vartani_grahan`, v323), reads a negative number (`grahan`,
v324), makes a `kosh` 800,000 times inside a loop (v317-v319), and uses a `mandapa` block (v320).

```powershell
sutram accept.sm accept.exe
"Asha Patel", "-5" | .\accept.exe
```

**You should see exactly:**

```
Siddh: 3827 baait sankalit
nama? Namaste, Asha Patel!
sankhya: -5  yoga: 800007
smriti: 128
```

| if you see | it means | fatal? |
|---|---|---|
| a message containing `Sutram truti` instead of `Siddh` | the compiler refused the program | **Yes.** Record the whole message. |
| `Siddh: ` with a number other than 3827 | the compiler made a different program | Not fatal by itself; record it and go on. |
| a Windows error box, or nothing printed, when `accept.exe` runs | the program does not run on this Windows | **Yes.** |
| `Namaste, Asha Patel` followed by anything other than `!` | the line was read with its line ending | **Yes** - `vartani_grahan` keeps the CR on Windows. |
| `sankhya: 5` | the minus sign was lost (the behaviour up to v323) | **Yes** - this compiler does not have v324's fix. |
| `yoga:` other than 800007 | a loop or a block computed something else | **Yes.** |
| the program never finishes (more than a minute) | | **Yes.** Press Ctrl+C; record it. |

## 6. The memory work - one number

`smriti.sm` makes a `kosh` 800,000 times in a loop and then prints `parimana()`: the bytes of memory the program
is holding at that moment. **Up to v316 every pass kept its `kosh`; from v317 the loop reuses one.**

```powershell
sutram smriti.sm smriti.exe
.\smriti.exe
```

**You should see exactly:**

```
Siddh: 2119 baait sankalit
yoga: 800000
smriti: 64
```

**The whole test is the last line.** `smriti: 64` is the memory work; **`smriti: 51200000` is the old behaviour**
(v315 and v316 print that - measured on Linux) and means this compiler does not have it. **Fatal.**

**What this step does not check:** the memory Windows itself reports for the program (Task Manager, the "working
set"). `parimana()` counts what the program's own allocator holds; that is the claim being tested, and it can be
read from the output. A Task Manager figure cannot be compared to an expected value here, so it is not asked for.

## 7. The lexer work - a curly quote is refused

`curly.sm` is `likha(“namaste”)` - with the curly quotation marks a word processor makes, not the straight `"`
that Sutram uses. **Up to v320 the compiler silently passed over characters it did not know; from v321 it refuses
them, naming the character.**

```powershell
sutram curly.sm curly.exe
$LASTEXITCODE
Test-Path curly.exe
```

**You should see:**

```
curly.sm:2:11: Sutram truti [E_AGYAT_AKSHAR]: agyat akshar '“' (U+201C)
      likha(“namaste”)
            ^
Sanket: saral uddharana-chihnam " (U+0022) likhyatam
1
False
```

**Two parts of this may look different, and that is not a failure:** the quotation mark between `'` and `'` on
the first line, and the two in the second line. The compiler writes them as UTF-8 bytes, and the PowerShell window
shows them according to its own code page - as `“`, or as two or three other characters (for example `â€œ`).
**Everything else must match exactly**: `curly.sm:2:11:`, `[E_AGYAT_AKSHAR]`, `(U+201C)`, the `^` under the
first quotation mark (column 11), the `Sanket` line, `1`, and `False`.

| if you see | it means | fatal? |
|---|---|---|
| `Siddh: ... baait sankalit` | the program was compiled - the character was not refused | **Yes - the lexer work is not in this compiler.** |
| `[E_UNDEFINED_NAME]: agyat naam 'namaste'` | the old behaviour (v315-v320 refuse it for another reason, at column 12) | **Yes.** |
| `0` instead of `1` | refused, but the compiler said it succeeded | **Yes.** |
| `True` | refused, but an executable was written anyway | **Yes.** |

## 8. The file-handling checks of v316 - one script, 18 steps

v316 makes the compiler refuse to write its output over its own source. That is checked by a script in the
repository, not by the installed copy. **The script needs four files from the pinned commit and nothing else:**

```powershell
$r = Join-Path $env:TEMP 'sutram-v316'
foreach ($f in 'win', 'lib', 'tests\windows') { New-Item -ItemType Directory -Force -Path (Join-Path $r $f) | Out-Null }
$u = 'https://github.com/dap2810/sutram/raw/c3b7b9ef185cfbe7e5a65d205f36a85bb195e168/'
foreach ($f in 'win/sutram.exe', 'sutram-link.exe', 'lib/ganit.smlib', 'tests/windows/accept_v316.cmd') {
    Invoke-WebRequest -Uri ($u + $f) -OutFile (Join-Path $r $f)
}
$b = Join-Path $r 'tests\windows\accept_v316.cmd'
[IO.File]::WriteAllText($b, ([IO.File]::ReadAllText($b) -replace "`r?`n", "`r`n"))
Set-Location $r
foreach ($f in 'win\sutram.exe', 'sutram-link.exe', 'lib\ganit.smlib', 'tests\windows\accept_v316.cmd') { (Get-FileHash $f -Algorithm SHA256).Hash + '  ' + $f }
cmd /c tests\windows\accept_v316.cmd
```

**The second-last line before `Set-Location` matters:** GitHub serves the script with Unix line ends (the
repository stores it that way and converts it only when it is checked out), and `cmd.exe` can lose a label in
such a file. The line rewrites it with Windows line ends, which is the file that was tested.
(Not the whole repository as a zip: a few of its file names are so long that, unpacked under your temporary
folder, they pass Windows' 260-character limit and the unpacking stops.)

**The four hash lines must be exactly:**

```
F22FEA3FEEFB0547816494EE53C4F6DB878FB471C563E4776D0AA029FF252304  win\sutram.exe
C36D79EE3CC870D466EAA0DEAE559750A1892CD60C90CD1AFE496D4EF0A28CE1  sutram-link.exe
ADEC447201E9F7B543E2720D24F33A2B3F1D6472ADFFBCF3191359675712CBD8  lib\ganit.smlib
3E78CDBE2240D219FFD4FC52148EC66A05283753F89CF43921F1FDDEDD9BB1C7  tests\windows\accept_v316.cmd
```

The first is the same as step 3's: **the script tests the same compiler that was installed.** A different hash on
any line: the download is not the tested file - stop and record it.

**You should see these 19 lines at the end** (there may be lines before them):

```
FAIL  01 the compiler starts and is v316 - GetFileInformationByHandle, SetEndOfFile and GetFileType were found
PASS  02 an ordinary compile is not refused on this disk, and its program prints 42
PASS  03 the source as its own output: refused, exit 1, the source unchanged
PASS  04 the source as .\name: refused, exit 1, the source unchanged
PASS  05 the source in another case, on a file system that ignores case: refused, exit 1, the source unchanged
PASS  06 the source by its full path: refused, exit 1, the source unchanged
PASS  07 the source through a folder and back: refused, exit 1, the source unchanged
PASS  08 a hard link to the source: refused, exit 1, the source unchanged
PASS  09 --object with the source as its output: refused, exit 1, the source unchanged
PASS  10 a program with yoj compiles and prints 9
PASS  11 the output naming a yoj module the compile read: refused, exit 1, the module unchanged
PASS  12 an existing larger output is replaced exactly - no old bytes left after the new program
PASS  13 an output in a folder that does not exist: an error, exit 1
PASS  14 NUL as the output still works - a device is written as before
PASS  15 sutram-link with its object as the output: refused, exit 1, the object unchanged
PASS  16 an ordinary link works and its program prints 42
PASS  17 the linker replaces an existing larger output exactly
PASS  18 after every step the source is byte for byte what it was

v316 acceptance: 17 passed, 1 failed, 0 skipped
```

**Step 01 is expected to FAIL - read this before you worry.** The script was written for v316, and step 01 checks
that the version line says `(v316)`. This compiler says `(v326)`, so 01 fails on the version text alone. What step
01 was really for - the compiler starts on Windows - is already shown by step 3. **Any other FAIL is fatal.** A
`SKIP` on step 08 means this disk does not allow hard links; not fatal - record it.

The script writes its result to `accept-v316-result.txt` in that folder (`%TEMP%\sutram-v316`). It contains no paths and is safe to send
as it is.

## 9. Uninstall

Settings -> Apps -> Installed apps. **There must be an entry `Sutram`**, publisher *Sutram Project*, version
**`1.0.326`** - record what it shows. Choose ... -> **Uninstall**. **You should see a message: *"Sutram was removed
from this user account."*** Then open a **new** PowerShell window:

```powershell
Test-Path (Join-Path $env:LOCALAPPDATA 'Programs\Sutram')
Get-Command sutram -ErrorAction SilentlyContinue
Test-Path (Join-Path $env:TEMP 'sutram-accept\accept.sm')
```

**You should see:**

```
False
True
```

(three commands, two lines: the second command prints nothing when `sutram` is gone.)

| if you see | it means | fatal? |
|---|---|---|
| *"Sutram could not be fully removed."* | the uninstaller failed | **Yes.** Record it. |
| `True` on the first line | the program folder is still there | **Yes.** |
| a line showing a path to `sutram.exe` | the PATH entry was not removed, or another Sutram remains | **Yes.** |
| `False` on the last line | the uninstall deleted a file it did not create | **Yes - the worst failure on this page.** |

**What this step does not check:** the Start menu entries and the rest of the user's PATH. Look in the Start menu:
the four Sutram entries (*Sutram IDE*, *Sutram Terminal*, *Sutram Documentation*, *Uninstall Sutram*) should be
gone. Record what you saw.

## 10. The record - fill this in and send it back

Copy this block, fill in each line with what you **saw**, and send it. Write `as expected` only when the screen
matched the grey block exactly.

```
Sutram Windows acceptance - installer 160a1ab6f38b, commit c3b7b9ef
Date:
Windows: 10 / 11 (edition only - no build number)
Account: ordinary user / administrator
1  download hash:
2  SmartScreen shown? yes / no      User Account Control prompt? yes / no      antivirus? none / message:
2  wizard pages as in the table? yes / differences:
2  finished with "Sutram has been installed successfully."? yes / no - message:
3  sutram --version:
3  path:                                 hash:
4  the three file hashes:
5  accept.exe output (4 lines):
6  smriti.exe output (3 lines):
7  curly.sm output (6 lines; the quotation marks shown as):
8  the four hashes as expected? yes / no:     accept_v316.cmd last line:
8  any FAIL other than 01:
9  Installed apps showed: name            publisher            version
9  "Sutram was removed from this user account."? yes / no - message:
9  the three lines:
9  Start menu entries gone? yes / no
Anything else you noticed:
```

## What this run does not check

- **The Sutram IDE** (the editor window) - it is installed, but nothing above opens it, and what it shows cannot be
  compared to a fixed text. Opening it from the Start menu, typing a program and running it is worth doing; record
  what happened, in words.
- **Programs that call the operating system in other ways** (sockets, the foreign-function interface, linking
  several files beyond step 8) - covered on Linux and under Wine only.
- **Performance** - the numbers in the project's benchmarks are Linux numbers.
