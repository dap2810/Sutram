# Sutram for Windows

## Option 1: Quick Install (no tools needed)

1. Double-click `windows\install.bat`
2. Done! Open a **new** Command Prompt and type `sutram --version`

This installs to `%LOCALAPPDATA%\Sutram` (no admin needed), adds to PATH,
and gives `.sm` files the Sutram icon.

## Option 2: Build a Professional .exe Installer (NSIS)

For a proper Windows installer with a beautiful wizard UI:

### Step 1: Install NSIS (one time, 2 minutes)
Download from: https://nsis.sourceforge.io/Download
(Or: `winget install NSIS.NSIS` or `choco install nsis`)

### Step 2: Prepare the files
Run this from the project root on Windows:
```
build-installer.bat
```
This creates the proper directory structure for NSIS.

### Step 3: Compile the installer
Right-click `windows\sutram-installer.nsi` → "Compile NSIS Script"

Or from command line:
```
makensis windows\sutram-installer.nsi
```

This produces `Sutram-Setup-1.0.exe` — a professional installer with:
- Welcome page with Sutram branding
- Component selection (compiler, language packs, examples, books)
- Automatic PATH setup (system-wide)
- .sm file association with the Sutram icon
- Start Menu + Desktop shortcuts
- Clean uninstaller

## Requirements

- **Windows 10 or 11** (64-bit)
- **WSL** (Windows Subsystem for Linux) — the Sutram compiler is a native
  Linux ELF binary. It runs on Windows through WSL at full speed.

Don't have WSL? Open **PowerShell as Administrator** and run:
```powershell
wsl --install
```
Then restart your computer.

## After Installation

```
sutram --version                    # check installation
sutram -i                           # interactive shell (like Python IDLE)
sutram hello.sm hello.bin           # compile a program
hello.bin                           # run it (via WSL)

# Use your language:
set SUTRAM_LANG=hindi               # Hindi keywords
set SUTRAM_LANG=tamil               # Tamil keywords
set SUTRAM_LANG=gujarati            # Gujarati keywords
sutram namaste.sm out.bin           # compiles with your keywords!
```

## The Sutram Icon

The icon represents the "sacred thread" (सूत्रम् = thread):
- **Deep teal** background — the color of knowledge (विद्या)
- **Golden spiral thread** — the sutra itself, weaving through the language
- **Central bindu** — the point of creation

After installation, all `.sm` files on your system display this icon.
