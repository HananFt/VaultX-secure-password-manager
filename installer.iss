[Setup]
AppName=VaultX
AppVersion=1.1.0
AppPublisher=HananFt
DefaultDirName={localappdata}\VaultX
DefaultGroupName=VaultX
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=VaultX-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
SetupIconFile=vault.ico
UninstallDisplayIcon={app}\VaultX.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copy the compiled PyInstaller executable
Source: "dist\VaultX.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\VaultX"; Filename: "{app}\VaultX.exe"
Name: "{group}\Uninstall VaultX"; Filename: "{uninstallexe}"
Name: "{commondesktop}\VaultX"; Filename: "{app}\VaultX.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\VaultX.exe"; Description: "{cm:LaunchProgram,VaultX}"; Flags: nowait postinstall skipifsilent