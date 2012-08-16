
;This file is part of pymecavideo.
;
; Copyright (C) 2009-2012 Cédrick FAURY
;
;pymecavideo is free software; you can redistribute it and/or modify
;it under the terms of the GNU General Public License as published by
;the Free Software Foundation; either version 2 of the License, or
;(at your option) any later version.
;
;pymecavideo is distributed in the hope that it will be useful,
;but WITHOUT ANY WARRANTY; without even the implied warranty of
;MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;GNU General Public License for more details.
;
;You should have received a copy of the GNU General Public License
;along with pymecavideo; if not, write to the Free Software
;Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

[Setup]
;Informations générales sur l'application
AppName=pymecavideo 6
AppVerName=pymecavideo 6.0
AppVersion=6.0
AppPublisher=Georges Khaznadar et Jean-Baptiste Butet
AppCopyright=Copyright (C) 2007-2012 Georges Khaznadar <georgesk@ofset.org> Jean-Baptiste Butet <ashashiwa@gmail.com>
VersionInfoVersion = 6.0.0.1

;Répertoire de base contenant les fichiers
SourceDir=D:\Developpement\pymecavideo_6

;Repertoire d'installation
DefaultDirName={pf}\pymecavideo
DefaultGroupName=pymecavideo
LicenseFile=gpl-3.0.txt

;Paramètres de compression
;lzma ou zip
Compression=lzma/max
SolidCompression=yes

;Par défaut, pas besoin d'être administrateur pour installer
PrivilegesRequired=none

;Nom du fichier généré et répertoire de destination
OutputBaseFilename=pymecavideo_6.0beta1_setup
OutputDir=releases

;Dans le panneau de configuration de Windows2000/NT/XP, c'est l'icone de pymecavideo.exe qui
;apparaît à gauche du nom du fichier pour la désinstallation
UninstallDisplayIcon={app}\data\icones\pymecavideo.ico

;Fenêtre en background
WindowResizable=false
WindowStartMaximized=true
WindowShowCaption=true
BackColorDirection=lefttoright


AlwaysUsePersonalGroup=no

[Languages]
Name: en; MessagesFile: "compiler:Default.isl"
Name: fr; MessagesFile: "compiler:Languages\French.isl"

;Name: fr; MessagesFile: "compiler:Languages\French.isl"

[Messages]
BeveledLabel=pymecavideo 6.0 installation


[CustomMessages]
;
; French
;
fr.uninstall=Désinstaller
fr.gpl_licence=Prendre connaissance du contrat de licence pour le logiciel
fr.fdl_licence=Prendre connaissance du contrat de licence pour la documentation associée
fr.CreateDesktopIcon=Créer un raccourci sur le bureau vers
fr.AssocFileExtension=&Associer le programme pymecavideo à l'extension .mecavideo
fr.CreateQuickLaunchIcon=Créer un icône dans la barre de lancement rapide
fr.FileExtensionName=Fichier pymecavideo
fr.InstallFor=Installer pour :
fr.AllUsers=Tous les utilisateurs
fr.JustMe=Seulement moi
fr.ShortCut=Raccourcis :
fr.Association=Association de fichier :
;fr.ffmpeg_ffplay = Outils video : ffmpeg et ffplay
fr.HelpFiles = Fichiers d'aide
fr.ExampleFiles = Fichiers d'exemple

;
; English
;
en.uninstall=Uninstall
en.gpl_licence=Read the GNU GPL
en.fdl_licence=Read the GNU FDL
en.AssocFileExtension=&Associate pymecavideo with .mecavideo extension
en.CreateDesktopIcon=Create Desktop shortcut to
en.CreateQuickLaunchIcon=Create a &Quick Launch icon to
en.FileExtensionName=pymecavideo file
en.InstallFor=Install for :
en.AllUsers=All users
en.JustMe=Just me
en.ShortCut=Short cuts :
en.Association=File association :
;en.ffmpeg_ffplay = ffmpeg and ffplay video tools
en.HelpFiles = Help Files
en.ExampleFiles = Example Files


[Types]
;Name: "full"; Description: "Full installation"
;Name: "compact"; Description: "Compact installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "program"; Description: "pymecavideo"; Types: custom; Flags: fixed
;Name: "ff"; Description: {cm:ffmpeg_ffplay}; Types: custom
Name: "help"; Description: {cm:HelpFiles}; Types: custom
Name: "exemple"; Description: {cm:ExampleFiles}; Types: custom
;Name: "readme\en"; Description: "English"; Flags: exclusive
;Name: "readme\de"; Description: "German"; Flags: exclusive

[Files]
;
; Fichiers de la distribution
;
Source: src\dist\*.*; DestDir: {app}\bin; Flags : ignoreversion recursesubdirs;
Source: *.txt; DestDir: {app}; Flags : ignoreversion;
Source: data\help\*.*; DestDir: {app}\data\help; Flags : ignoreversion recursesubdirs; Components : help
Source: data\video\*.*; DestDir: {app}\data\video; Flags : ignoreversion recursesubdirs; Components : exemple
Source: data\icones\*.*; DestDir: {app}\data\icones; Flags : ignoreversion recursesubdirs
Source: data\lang\*.*; DestDir: {app}\data\lang; Flags : ignoreversion recursesubdirs
;Source: ff*.exe; DestDir: {app}; Flags : ignoreversion; Components : ff


[Tasks]
Name: desktopicon2; Description: {cm:CreateDesktopIcon} pyMecaVideo ;GroupDescription: {cm:ShortCut}; MinVersion: 4,4
Name: fileassoc; Description: {cm:AssocFileExtension};GroupDescription: {cm:Association};
Name: common; Description: {cm:AllUsers}; GroupDescription: {cm:InstallFor}; Flags: exclusive
Name: local;  Description: {cm:JustMe}; GroupDescription: {cm:InstallFor}; Flags: exclusive unchecked

[Icons]
Name: {group}\pymecavideo;Filename: {app}\bin\pymecavideo.exe; WorkingDir: {app}\bin; IconFileName: {app}\bin\pymecavideo.exe
Name: {group}\{cm:uninstall} pymecavideo; Filename: {app}\unins000.exe;IconFileName: {app}\unins000.exe
;
; On ajoute sur le Bureau l'icône pymecavideo
;
Name: {code:DefDesktop}\pymecavideo 6.0;   Filename: {app}\bin\pymecavideo.exe; WorkingDir: {app}\bin; MinVersion: 4,4; Tasks: desktopicon2; IconFileName: {app}\bin\pymecavideo.exe


[_ISTool]
Use7zip=true


[Registry]
; Tout ce qui concerne les fichiers .mecavideo
Root: HKCR; SubKey: .mecavideo; ValueType: string; ValueData: {cm:FileExtensionName}; Flags: uninsdeletekey
Root: HKCR; SubKey: {cm:FileExtensionName}; ValueType: string; Flags: uninsdeletekey; ValueData: {cm:FileExtensionName}
Root: HKCR; SubKey: {cm:FileExtensionName}\Shell\Open\Command; ValueType: string; ValueData: """{app}\bin\pymecavideo.exe"" ""-f %1"""; Flags: uninsdeletekey;
Root: HKCR; Subkey: {cm:FileExtensionName}\DefaultIcon; ValueType: string; ValueData: {app}\data\icones\pymecavideo.ico,0; Flags: uninsdeletekey;

; Pour stocker le style d'installation : "All users" ou "Current user"
Root: HKLM; Subkey: Software\pymecavideo; ValueType: string; ValueName: DataFolder; ValueData: {code:DefAppDataFolder}\pymecavideo ; Flags: uninsdeletekey;



[Code]
Procedure URLLabelOnClick(Sender: TObject);
var
  ErrorCode: Integer;
begin
  ShellExec('open', 'http://outilsphysiques.tuxfamily.org/pmwiki.php/Oppl/pymecavideo', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
end;

{*** INITIALISATION ***}
Procedure InitializeWizard;
var
  URLLabel: TNewStaticText;
begin
  URLLabel := TNewStaticText.Create(WizardForm);
  URLLabel.Caption := 'pymecavideo Web Site';
  URLLabel.Cursor := crHand;
  URLLabel.OnClick := @URLLabelOnClick;
  URLLabel.Parent := WizardForm;
  { Alter Font *after* setting Parent so the correct defaults are inherited first }
  URLLabel.Font.Style := URLLabel.Font.Style + [fsUnderline];
  URLLabel.Font.Color := clBlue;
  URLLabel.Top := WizardForm.ClientHeight - URLLabel.Height - 15;
  URLLabel.Left := ScaleX(20);
end;


{ Renvoie le dossier "Application Data" à utiliser }
function DefAppDataFolder(Param: String): String;
begin
  if IsTaskSelected('common') then
    Result := ExpandConstant('{commonappdata}')
  else
    Result := ExpandConstant('{localappdata}')
end;


{ Renvoie le bureau sur lequel placer le raccourci de pyMecaVideo }
function DefDesktop(Param: String): String;
begin
  if IsTaskSelected('common') then
    Result := ExpandConstant('{commondesktop}')
  else
    Result := ExpandConstant('{userdesktop}')
end;















