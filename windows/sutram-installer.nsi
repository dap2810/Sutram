; ============================================================
; Sutram Installer for Windows — NSIS Script
; ============================================================
; Compile with NSIS 3.x:  makensis sutram-installer.nsi
; Download NSIS from:     https://nsis.sourceforge.io
; ============================================================

!define APPNAME "Sutram"
!define VERSION "1.0"
!define PUBLISHER "Sutram Project"
!define APPURL "https://sutram.dev"
!define EXENAME "sutram"
!define ASSOC_EXT ".sm"
!define ASSOC_KEY "Sutram.SourceFile"

Name "${APPNAME} ${VERSION}"
OutFile "Sutram-Setup-${VERSION}.exe"
InstallDir "$PROGRAMFILES64\${APPNAME}"
InstallDirRegKey HKLM "Software\${APPNAME}" "InstallDir"
RequestExecutionLevel admin

; --- Modern UI ---
!include "MUI2.nsh"
!define MUI_ICON "icons\sutram.ico"
!define MUI_UNICON "icons\sutram.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "installer-header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "installer-welcome.bmp"
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Open Sutram Shell (requires WSL)"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchShell"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\docs\sutram-book-english.html"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Open the Sutram Book (English)"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ============================================================
; Sections
; ============================================================

Section "Sutram Compiler (required)" SecCore
    SectionIn RO
    SetOutPath "$INSTDIR\bin"
    File "bin\sutram_compiler"
    File "bin\sutram.cmd"

    SetOutPath "$INSTDIR"
    File "LICENSE.txt"
    File "README.md"

    ; --- Registry entries ---
    WriteRegStr HKLM "Software\${APPNAME}" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\${APPNAME}" "Version" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} ${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\icons\sutram.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${PUBLISHER}"

    ; --- Add to PATH (system-wide) ---
    EnVar::SetHKLM
    EnVar::AddValue "Path" "$INSTDIR\bin"
    EnVar::Update

    ; --- Uninstaller ---
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; --- Start Menu shortcut ---
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Sutram Shell.lnk" "$INSTDIR\bin\sutram.cmd" "" "$INSTDIR\icons\sutram.ico" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Sutram Book.lnk" "$INSTDIR\docs\sutram-book-english.html" "" "$INSTDIR\icons\sutram.ico" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\icons\sutram.ico" 0

    ; --- Desktop shortcut ---
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\bin\sutram.cmd" "" "$INSTDIR\icons\sutram.ico" 0
SectionEnd

Section "Icon Pack" SecIcons
    SetOutPath "$INSTDIR\icons"
    File "icons\sutram.ico"
    File "icons\sutram-icon.svg"
    File "icons\sutram-256.png"

    ; --- Associate .sm files with Sutram icon ---
    WriteRegStr HKCR "${ASSOC_EXT}" "" "${ASSOC_KEY}"
    WriteRegStr HKCR "${ASSOC_KEY}" "" "Sutram Source File"
    WriteRegStr HKCR "${ASSOC_KEY}\DefaultIcon" "" "$INSTDIR\icons\sutram.ico"
    WriteRegStr HKCR "${ASSOC_KEY}\shell\open\command" "" '"$INSTDIR\bin\sutram.cmd" "compile" "%1"'
SectionEnd

Section "Language Packs (10 Indian languages)" SecLangs
    SetOutPath "$INSTDIR\lang"
    File "lang\hindi.lang"
    File "lang\telugu.lang"
    File "lang\bengali.lang"
    File "lang\tamil.lang"
    File "lang\marathi.lang"
    File "lang\gujarati.lang"
    File "lang\kannada.lang"
    File "lang\malayalam.lang"
    File "lang\punjabi.lang"
    File "lang\odia.lang"
SectionEnd

Section "Example Programs" SecExamples
    SetOutPath "$INSTDIR\examples"
    File "examples\*.sm"
SectionEnd

Section "Documentation (6 Books)" SecDocs
    SetOutPath "$INSTDIR\docs"
    File "docs\sutram-book-english.html"
    File "docs\sutram-book-hindi.html"
    File "docs\sutram-book-sanskrit.html"
    File "docs\sutram-book-telugu.html"
    File "docs\sutram-book-tamil.html"
    File "docs\sutram-book-gujarati.html"
SectionEnd

Section "Standard Library" SecLib
    SetOutPath "$INSTDIR\lib"
    File "lib\*.smlib"
SectionEnd

; ============================================================
; Functions
; ============================================================

Function LaunchShell
    Exec '"$INSTDIR\bin\sutram.cmd" "-i"'
FunctionEnd

; --- Uninstaller ---
Section "Uninstall"
    ; Remove from PATH
    EnVar::SetHKLM
    EnVar::DeleteValue "Path" "$INSTDIR\bin"
    EnVar::Update

    ; Remove file associations
    DeleteRegKey HKCR "${ASSOC_KEY}"
    DeleteRegKey HKCR "${ASSOC_EXT}"

    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKLM "Software\${APPNAME}"

    ; Remove files
    Delete "$INSTDIR\bin\sutram_compiler"
    Delete "$INSTDIR\bin\sutram.cmd"
    Delete "$INSTDIR\icons\sutram.ico"
    Delete "$INSTDIR\icons\sutram-icon.svg"
    Delete "$INSTDIR\icons\sutram-256.png"
    Delete "$INSTDIR\lang\*.lang"
    Delete "$INSTDIR\examples\*.sm"
    Delete "$INSTDIR\docs\*.html"
    Delete "$INSTDIR\lib\*.smlib"
    Delete "$INSTDIR\LICENSE.txt"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\uninstall.exe"

    ; Remove directories
    RMDir "$INSTDIR\bin"
    RMDir "$INSTDIR\icons"
    RMDir "$INSTDIR\lang"
    RMDir "$INSTDIR\examples"
    RMDir "$INSTDIR\docs"
    RMDir "$INSTDIR\lib"
    RMDir "$INSTDIR"

    ; Remove shortcuts
    Delete "$SMPROGRAMS\${APPNAME}\*.*"
    RMDir "$SMPROGRAMS\${APPNAME}"
    Delete "$DESKTOP\${APPNAME}.lnk"
SectionEnd
