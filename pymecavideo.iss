
;This file is part of pymecavideo.
;
; Copyright (C) 2009-2010 C�drick FAURY
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
;Informations g�n�rales sur l'application
AppName=pymecavideo 5
AppVerName=pymecavideo 5.2
AppVersion=5.2
AppPublisher=Georges Khaznadar et Jean-Baptiste Butet
AppCopyright=Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org> Jean-Baptiste Butet <ashashiwa@gmail.com>
VersionInfoVersion = 5.2.0.0

;R�pertoire de base contenant les fichiers
SourceDir=D:\Documents\Developpement\pyMecaVideo

;Repertoire d'installation
DefaultDirName={pf}\pyMecaVideo
DefaultGroupName=pyMecaVideo
LicenseFile=gpl-2.0.txt

;Param�tres de compression
;lzma ou zip
Compression=lzma/max
SolidCompression=yes

;Par d�faut, pas besoin d'�tre administrateur pour installer
PrivilegesRequired=none

;Nom du fichier g�n�r� et r�pertoire de destination
OutputBaseFilename=pyMecaVideo 5.2
OutputDir=releases

;Dans le panneau de configuration de Windows2000/NT/XP, c'est l'icone de pyMecaVideo.exe qui
;appara�t � gauche du nom du fichier pour la d�sinstallation
UninstallDisplayIcon={app}\data\icones\pyMecaVideo.ico

;Fen�tre en background
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
BeveledLabel=pyMecaVideo 5.2 installation


[CustomMessages]
;
; French
;
fr.uninstall=D�sinstaller
fr.gpl_licence=Prendre connaissance du contrat de licence pour le logiciel
fr.fdl_licence=Prendre connaissance du contrat de licence pour la documentation associ�e
fr.CreateDesktopIcon=Cr�er un raccourci sur le bureau vers
fr.AssocFileExtension=&Associer le programme pyMecaVideo � l'extension .mecavideo
fr.CreateQuickLaunchIcon=Cr�er un ic�ne dans la barre de lancement rapide
fr.FileExtensionName=Fichier pyMecaVideo
fr.InstallFor=Installer pour :
fr.AllUsers=Tous les utilisateurs
fr.JustMe=Seulement moi
fr.ShortCut=Raccourcis :
fr.Association=Association de fichier :
fr.ffmpeg_ffplay = Outils video : ffmpeg et ffplay
fr.HelpFiles = Fichiers d'aide
fr.ExampleFiles = Fichiers d'exemple

;
; English
;
en.uninstall=Uninstall
en.gpl_licence=Read the GNU GPL
en.fdl_licence=Read the GNU FDL
en.AssocFileExtension=&Associate pyMecaVideo with .mecavideo extension
en.CreateDesktopIcon=Create Desktop shortcut to
en.CreateQuickLaunchIcon=Create a &Quick Launch icon to
en.FileExtensionName=pyMecaVideo file
en.InstallFor=Install for :
en.AllUsers=All users
en.JustMe=Just me
en.ShortCut=Short cuts :
en.Association=File association :
en.ffmpeg_ffplay = ffmpeg and ffplay video tools
en.HelpFiles = Help Files
en.ExampleFiles = Example Files


[Types]
;Name: "full"; Description: "Full installation"
;Name: "compact"; Description: "Compact installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "program"; Description: "pyMecaVideo"; Types: custom; Flags: fixed
Name: "ff"; Description: {cm:ffmpeg_ffplay}; Types: custom
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
Source: ff*.exe; DestDir: {app}; Flags : ignoreversion; Components : ff


[Tasks]
Name: desktopicon2; Description: {cm:CreateDesktopIcon} pyMecaVideo ;GroupDescription: {cm:ShortCut}; MinVersion: 4,4
Name: fileassoc; Description: {cm:AssocFileExtension};GroupDescription: {cm:Association};
Name: common; Description: {cm:AllUsers}; GroupDescription: {cm:InstallFor}; Flags: exclusive
Name: local;  Description: {cm:JustMe}; GroupDescription: {cm:InstallFor}; Flags: exclusive unchecked

[Icons]
Name: {group}\pyMecaVideo;Filename: {app}\bin\pyMecaVideo.exe; WorkingDir: {app}\bin; IconFileName: {app}\bin\pyMecaVideo.exe
Name: {group}\{cm:uninstall} pyMecaVideo; Filename: {app}\unins000.exe;IconFileName: {app}\unins000.exe
;
; On ajoute sur le Bureau l'ic�ne pyMecaVideo
;
Name: {code:DefDesktop}\pyMecaVideo 5.2;   Filename: {app}\bin\pyMecaVideo.exe; WorkingDir: {app}\bin; MinVersion: 4,4; Tasks: desktopicon2; IconFileName: {app}\bin\pyMecaVideo.exe


[_ISTool]
Use7zip=true


[Registry]
; Tout ce qui concerne les fichiers .mecavideo
Root: HKCR; SubKey: .mecavideo; ValueType: string; ValueData: {cm:FileExtensionName}; Flags: uninsdeletekey
Root: HKCR; SubKey: {cm:FileExtensionName}; ValueType: string; Flags: uninsdeletekey; ValueData: {cm:FileExtensionName}
Root: HKCR; SubKey: {cm:FileExtensionName}\Shell\Open\Command; ValueType: string; ValueData: """{app}\bin\pyMecaVideo.exe"" ""%1"""; Flags: uninsdeletekey;
Root: HKCR; Subkey: {cm:FileExtensionName}\DefaultIcon; ValueType: string; ValueData: {app}\data\icones\pyMecaVideo.ico,0; Flags: uninsdeletekey;

; Pour stocker le style d'installation : "All users" ou "Current user"
Root: HKLM; Subkey: Software\pyMecaVideo; ValueType: string; ValueName: DataFolder; ValueData: {code:DefAppDataFolder}\pyMecaVideo ; Flags: uninsdeletekey;



[Code]
Procedure URLLabelOnClick(Sender: TObject);
var
  ErrorCode: Integer;
begin
  ShellExec('open', 'http://outilsphysiques.tuxfamily.org/pmwiki.php/Oppl/Pymecavideo', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
end;

{*** INITIALISATION ***}
Procedure InitializeWizard;
var
  URLLabel: TNewStaticText;
begin
  URLLabel := TNewStaticText.Create(WizardForm);
  URLLabel.Caption := 'PyMecaVideo Web Site';
  URLLabel.Cursor := crHand;
  URLLabel.OnClick := @URLLabelOnClick;
  URLLabel.Parent := WizardForm;
  { Alter Font *after* setting Parent so the correct defaults are inherited first }
  URLLabel.Font.Style := URLLabel.Font.Style + [fsUnderline];
  URLLabel.Font.Color := clBlue;
  URLLabel.Top := WizardForm.ClientHeight - URLLabel.Height - 15;
  URLLabel.Left := ScaleX(20);
end;


{ Renvoie le dossier "Application Data" � utiliser }
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











