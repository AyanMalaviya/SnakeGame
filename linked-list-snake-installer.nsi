; NSIS Installer Script for Linked List Snake
; To use this:
; 1. Download NSIS from https://nsis.sourceforge.io/
; 2. Right-click this file and select "Compile NSIS Script"
; 3. Or use: makensis.exe linked-list-snake-installer.nsi

; Include modern UI library
!include "MUI2.nsh"

; Basic Settings
Name "Linked List Snake"
OutFile "Linked_List_Snake_Installer.exe"
InstallDir "$PROGRAMFILES\Linked List Snake"
InstallDirRegKey HKCU "Software\Linked List Snake" "Install_Dir"

; UI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Installation section
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy main executable
    File "dist\Linked List Snake.exe"
    
    ; Copy game assets if they exist
    ${If} ${FileExists} "apple.png"
        File "apple.png"
    ${EndIf}
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\Linked List Snake"
    CreateShortCut "$SMPROGRAMS\Linked List Snake\Linked List Snake.lnk" "$INSTDIR\Linked List Snake.exe"
    CreateShortCut "$SMPROGRAMS\Linked List Snake\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortCut "$DESKTOP\Linked List Snake.lnk" "$INSTDIR\Linked List Snake.exe"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Registry entries
    WriteRegStr HKCU "Software\Linked List Snake" "Install_Dir" "$INSTDIR"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Linked List Snake" "DisplayName" "Linked List Snake"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Linked List Snake" "UninstallString" "$INSTDIR\Uninstall.exe"
SectionEnd

; Uninstall section
Section "Uninstall"
    Delete "$INSTDIR\Linked List Snake.exe"
    Delete "$INSTDIR\apple.png"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\Linked List Snake\Linked List Snake.lnk"
    Delete "$SMPROGRAMS\Linked List Snake\Uninstall.lnk"
    RMDir "$SMPROGRAMS\Linked List Snake"
    
    Delete "$DESKTOP\Linked List Snake.lnk"
    
    DeleteRegKey /ifempty HKCU "Software\Linked List Snake"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Linked List Snake"
SectionEnd
