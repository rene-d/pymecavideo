
;This file is part of pymecavideo.
;
; Copyright (C) 2009-2012 C�drick FAURY
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

#define AppVersion "7.2.1.0"


[Setup]
;Informations g�n�rales sur l'application
AppName=pymecavideo {#AppVersion}
AppVerName=pymecavideo {#AppVersion}
AppVersion={#AppVersion}
AppPublisher=Georges Khaznadar et Jean-Baptiste Butet
AppCopyright=Copyright (C) 2007-2030 Georges Khaznadar <georgesk.debian.org>
VersionInfoVersion = 7.2.1.0

;R�pertoire de base contenant les fichiers
SourceDir=C:\Users\JB\Documents\pymecavideo

;Repertoire d'installation
DefaultDirName={pf}\pymecavideo
DefaultGroupName=pymecavideo
LicenseFile=COPYING

;Param�tres de compression
;lzma ou zip
Compression=lzma/max
SolidCompression=yes

;Par d�faut, pas besoin d'�tre administrateur pour installer
PrivilegesRequired=none

;Nom du fichier g�n�r� et r�pertoire de destination
OutputBaseFilename=pymecavideo_{#AppVersion}_setup
OutputDir=releases

;Dans le panneau de configuration de Windows2000/NT/XP, c'est l'icone de pymecavideo.exe qui
;appara�t � gauche du nom du fichier pour la d�sinstallation
UninstallDisplayIcon={app}\data\icones\icone_pymecavideo.ico

;Fen�tre en background
WindowResizable=false
WindowStartMaximized=true
WindowShowCaption=true
BackColorDirection=lefttoright

WizardImageFile=data\icones\pymecavideo_setup.bmp

AlwaysUsePersonalGroup=no

[Languages]
Name: en; MessagesFile: "compiler:Default.isl"
Name: fr; MessagesFile: "compiler:Languages\French.isl"
Name: es; MessagesFile: "compiler:Languages\Spanish.isl"

;Name: fr; MessagesFile: "compiler:Languages\French.isl"
 
[Messages]
BeveledLabel=pymecavideo {#AppVersion} installation


[CustomMessages]
;
; French
;
fr.uninstall=D�sinstaller
fr.gpl_licence=Prendre connaissance du contrat de licence pour le logiciel
fr.fdl_licence=Prendre connaissance du contrat de licence pour la documentation associ�e
fr.CreateDesktopIcon=Cr�er un raccourci sur le bureau vers
fr.AssocFileExtension=&Associer le programme pymecavideo � l'extension .mecavideo
fr.CreateQuickLaunchIcon=Cr�er un ic�ne dans la barre de lancement rapide
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

;
; Espanol
;
en.uninstall=Desinstalaci�n
en.gpl_licence=Leer el contrato de licencia para el software
en.fdl_licence=Leer el contrato de licencia para la documentaci�n
en.AssocFileExtension=&Asociar pymecavideo con extensi�n .mecavideo
en.CreateDesktopIcon=Crear acceso directo del escritorio a
en.CreateQuickLaunchIcon=Crear un icono de inicio r�pido para
en.FileExtensionName=pymecavideo archivo
en.InstallFor=Instalar para :
en.AllUsers=Todos los usuarios
en.JustMe=S�lo yo
en.ShortCut=Accesos :
en.Association=Asociaci�n de archivo :
;en.ffmpeg_ffplay = ffmpeg and ffplay video tools
en.HelpFiles = Archivos de ayuda
en.ExampleFiles = Archivos de ejemplo



[Types]
;Name: "full"; Description: "Full installation"
;Name: "compact"; Description: "Compact installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "program"; Description: "pymecavideo"; Types: custom; Flags: fixed
Name: "help"; Description: {cm:HelpFiles}; Types: custom
Name: "exemple"; Description: {cm:ExampleFiles}; Types: custom
;Name: "readme\en"; Description: "English"; Flags: exclusive
;Name: "readme\de"; Description: "German"; Flags: exclusive

[Files]
;
; Fichiers de la distribution
;
Source: src\build/*.*;    DestDir: {app};           Flags : ignoreversion recursesubdirs;

[Tasks]
Name: desktopicon2; Description: {cm:CreateDesktopIcon} pymecavideo ;GroupDescription: {cm:ShortCut}; MinVersion: 4,4
Name: fileassoc; Description: {cm:AssocFileExtension};GroupDescription: {cm:Association};
Name: common; Description: {cm:AllUsers}; GroupDescription: {cm:InstallFor}; Flags: exclusive
Name: local;  Description: {cm:JustMe}; GroupDescription: {cm:InstallFor}; Flags: exclusive unchecked

[Icons]
Name: {group}\pymecavideo;Filename: {app}\pymecavideo.exe; WorkingDir: {app}; IconFileName: {app}\pymecavideo.exe
Name: {group}\{cm:uninstall} pymecavideo; Filename: {app}\unins_pmv.exe;IconFileName: {app}\unins_pmv.exe
;
; On ajoute sur le Bureau l'ic�ne pymecavideo
;
Name: {code:DefDesktop}\pymecavideo {#AppVersion};   Filename: {app}\pymecavideo.exe; WorkingDir: {app}; MinVersion: 4,4; Tasks: desktopicon2; IconFileName: {app}\pymecavideo.exe


[_ISTool]
Use7zip=true


[Registry]
; Tout ce qui concerne les fichiers .mecavideo
Root: HKCR; SubKey: .mecavideo; ValueType: string; ValueData: {cm:FileExtensionName}; Flags: uninsdeletekey
Root: HKCR; SubKey: {cm:FileExtensionName}; ValueType: string; Flags: uninsdeletekey; ValueData: {cm:FileExtensionName}
Root: HKCR; SubKey: {cm:FileExtensionName}\Shell\Open\Command; ValueType: string; ValueData: """{app}\pymecavideo.exe"" ""-f %1"""; Flags: uninsdeletekey;
Root: HKCR; Subkey: {cm:FileExtensionName}\DefaultIcon; ValueType: string; ValueData: {app}\data\icones\icone_pymecavideo.ico,0; Flags: uninsdeletekey;

; Pour stocker le style d'installation : "All users" ou "Current user"
Root: HKLM; Subkey: Software\pymecavideo; ValueType: string; ValueName: DataFolder; ValueData: {code:DefAppDataFolder}\pymecavideo ; Flags: uninsdeletekey;



[Code]
Procedure URLLabelOnClick(Sender: TObject);
var
  ErrorCode: Integer;
begin
  ShellExec('open', 'https://gitlab.com/oppl/pymecavideo', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
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


{ Renvoie le dossier "Application Data" � utiliser }
function DefAppDataFolder(Param: String): String;
begin
  if IsTaskSelected('common') then
    Result := ExpandConstant('{commonappdata}')
  else
    Result := ExpandConstant('{localappdata}')
end;


{ Renvoie le bureau sur lequel placer le raccourci de pymecavideo }
function DefDesktop(Param: String): String;
begin
  if IsTaskSelected('common') then
    Result := ExpandConstant('{commondesktop}')
  else
    Result := ExpandConstant('{userdesktop}')
end;















