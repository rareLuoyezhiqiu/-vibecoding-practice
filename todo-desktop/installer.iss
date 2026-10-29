; 待办清单 安装包脚本（Inno Setup 6）
; 编译：ISCC.exe installer.iss

#define MyAppName "待办清单"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "rareLuoyezhiqiu"
#define MyAppExeName "TodoList.exe"

[Setup]
; AppId 用来识别同一个应用的不同版本，升级时保持不变
AppId={{29D8341A-706F-4BBE-B486-8A51C180848A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\TodoList
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; 按用户安装，不需要管理员权限，不会弹 UAC
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=TodoList-Setup-{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
; 只支持 64 位 Windows（打包出的 exe 是 64 位）
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinesesimp"; MessagesFile: "ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
