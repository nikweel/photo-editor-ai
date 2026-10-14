#define Ver GetEnv("APP_VERSION")
[Setup]
AppName=Photo Editor AI
AppVersion={#Ver}
AppPublisher=Nikolay Fedotov
AppPublisherURL=https://github.com/nikweel/photo-editor-ai
DefaultDirName={autopf}\Photo Editor AI
DefaultGroupName=Photo Editor AI
OutputDir=..\release
OutputBaseFilename=Photo-Editor-AI-{#Ver}-Setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\Photo-Editor-AI.exe
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "ru"; MessagesFile: "compiler:Languages\Russian.isl"
[Files]
Source: "..\dist\Photo-Editor-AI\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
[Icons]
Name: "{group}\Photo Editor AI"; Filename: "{app}\Photo-Editor-AI.exe"
Name: "{autodesktop}\Photo Editor AI"; Filename: "{app}\Photo-Editor-AI.exe"
[Run]
Filename: "{app}\Photo-Editor-AI.exe"; Description: "{cm:LaunchProgram,Photo Editor AI}"; Flags: nowait postinstall skipifsilent
