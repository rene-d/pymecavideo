#!/bin/env python

from __future__ import print_function

from subprocess import check_call, Popen, PIPE
import shutil
import os
import sys
import urllib
import urllib2
from optparse import Option, OptionParser


# paths
PYINSTALLERDIR = r"C:\Documents and Settings\Administrateur\Bureau\trunk"
PYTHON = 'c:\Python26\python.exe'
ZIP7 = r'c:\Program Files\7-Zip\7z.exe'

FNAME_NORMAL_CHANNEL = 'release_info.txt'
FNAME_BETA_CHANNEL = 'release_info_beta.txt'
FNAME_DEV_CHANNEL = 'release_info_dev.txt'
FNAME_NORMAL_BACKUP = 'release_info.txt.bak'

LINE_DATE = 0
LINE_VERSION = 1
LINE_URL = 2
LINE_WIN_EXE = 3
LINE_WIN_ZIP = 4


def replace_release_line(lineNb, lineText):
    lines = open(FNAME_NORMAL_CHANNEL, 'r').readlines()
    # backup
    open(FNAME_NORMAL_BACKUP, 'w').write(''.join(lines))
    if lineText[-1] != '\n':
        lineText += '\n'
    lines[lineNb] = lineText
    open(FNAME_NORMAL_CHANNEL, 'wb').write(''.join(lines))


# global definitions
def setglobal():
    global PYMECAVIDEO_VER, PYMECAVIDEO_VER_ZIP, PYMECAVIDEO_PACKAGED, SOURCEDIR, SOURCEDIR_ZIP, DIR_RELEASE_DEV, DIR_RELEASE_DEVw, INSTALLER_NAME
    PYMECAVIDEO_VER = 'pymecavideo-4.1'
    PYMECAVIDEO_VER_ZIP = PYMECAVIDEO_VER + '.zip'
    PYMECAVIDEO_PACKAGED = 'pymecavideo-packaged'
    SOURCEDIR = 'pymecavideo-source-4.1'
    SOURCEDIR_ZIP = SOURCEDIR + '.zip'
    DIR_RELEASE_DEV = '../../release-dev/'
    DIR_RELEASE_DEVw = '..\\..\\release-dev\\'
    INSTALLER_NAME = "Installeur PYMECAVIDEO 4.1"


def safe_unlink(f):
    if os.path.exists(f):
        os.unlink(f)
    assert not os.path.exists(f)


def safe_rmtree(f):
    if os.path.exists(f):
        shutil.rmtree(f)
    assert not os.path.exists(f)


def report(s):
    print('============>', s)


def make_exe(options):
    report('%s mode' % ('DEBUG' if options.debug else 'RELEASE'))
    safe_rmtree('exe/dist/PYMECAVIDEO/data')
    if not options.debug:
        safe_rmtree('exe/dist/PYMECAVIDEO/')

    consoleArg = {False: '--window', True: '--console'}[bool(options.console)]
    report('packaging with ' + consoleArg)
    check_call([PYTHON, PYINSTALLERDIR + '\Makespec.py',
                consoleArg,
                '--onedir',
                'src\pymecavideo.py',
                '-o', 'exe',
                '--icon=data\icones\pymecavideo.ico'])
    check_call([PYTHON, PYINSTALLERDIR + '/Build.py', 'exe/pymecavideo.spec'])
    # os.unlink( 'exe/distpymecavideo/_socket.pyd' )
    # os.unlink( 'exe/distpymecavideo/_ssl.pyd' )
    # os.unlink( 'exe/distpymecavideo/bz2.pyd' )
    # os.unlink( 'exe/distpymecavideo/win32api.pyd' )
    # os.unlink( 'exe/distpymecavideo/win32evtlog.pyd' )
    # shutil.rmtree( 'exe/distpymecavideo/qt4_plugins' )
    # shutil.copy( 'LISEZMOI.TXT',  'exe/distpymecavideo' )
    # shutil.copy( 'LICENSE.TXT','exe/distpymecavideo/')
    shutil.copytree('data', 'exe/distpymecavideo/data')
    if options.debug:
        file('exe/dist/PYMECAVIDEO/PYMECAVIDEO-debug.bat', 'w').write('''
PYMECAVIDEO.exe --debug
''')
        shutil.copy('config-bluebird.ini',
                    'exe/dist/PYMECAVIDEO/PYMECAVIDEO-config.ini')
    report('Exe ready in exe/dist/PYMECAVIDEO')


def make_zip_exe(options):
    make_exe(options)
    orig_path = os.getcwd()
    os.chdir('exe\dist')
    safe_rmtree(PYMECAVIDEO_VER)
    shutil.move('PYMECAVIDEO', PYMECAVIDEO_VER)
    zip_target = '..\\..\\' + DIR_RELEASE_DEVw + PYMECAVIDEO_VER_ZIP
    safe_unlink(zip_target)
    compLevel = 0 if options.debug else 9
    check_call([ZIP7, 'a', '-mx=%d' % compLevel, zip_target, PYMECAVIDEO_VER])
    os.chdir('../..')
    safe_rmtree('exe')
    check_call([ZIP7, 'x', '-y', DIR_RELEASE_DEVw + PYMECAVIDEO_VER_ZIP])
    shutil.rmtree(PYMECAVIDEO_VER)
    os.chdir(orig_path)
    report('%s ready' % PYMECAVIDEO_VER_ZIP)


def test_zip(options):
    orig_path = os.getcwd()
    check_call([ZIP7, 'x', '-aoa', DIR_RELEASE_DEVw + PYMECAVIDEO_VER_ZIP])
    os.chdir(PYMECAVIDEO_VER)
    check_call(['PYMECAVIDEO.exe', '--autosimu'])
    os.chdir('..')
    shutil.rmtree(PYMECAVIDEO_VER)
    report('%s tested successfully' % PYMECAVIDEO_VER_ZIP)


def make_inst(options):
    make_exe(options)
    # with gui
    # ISS_COMPILER=r'c:\Program Files\Inno Setup 5\Compil32.exe'
    # text based
    ISS_COMPILER = r'c:\Program Files\Inno Setup 5\ISCC.exe'
    ISS_SRC_FILE = 'PYMECAVIDEO-inno.in.iss'
    ISS_DEST_FILE = 'PYMECAVIDEO-inno.iss'
    open(ISS_DEST_FILE, 'w').write(open(ISS_SRC_FILE).read() % {
        'V': 4.1,
        'compression': 'none' if options.debug else 'lzma',
        'outputDir': DIR_RELEASE_DEVw,
        'InstallerName': INSTALLER_NAME,
    })
    check_call([ISS_COMPILER,
                # '/cc',
                ISS_DEST_FILE])
    os.unlink(ISS_DEST_FILE)


def make_zip_src(options):
    safe_rmtree(SOURCEDIR)
    check_call(['hg', 'clone', '..', SOURCEDIR])
    shutil.rmtree(SOURCEDIR + '/.hg')
    os.chdir(SOURCEDIR)
    shutil.move('PYMECAVIDEO', SOURCEDIR)
    check_call([ZIP7, 'a', '../' + DIR_RELEASE_DEV + SOURCEDIR_ZIP, SOURCEDIR])
    os.chdir('..')
    shutil.rmtree(SOURCEDIR)
    report('%s ready' % SOURCEDIR_ZIP)


def test_src(options):
    orig_path = os.getcwd()
    check_call([ZIP7, 'x', '-aoa', DIR_RELEASE_DEV + SOURCEDIR_ZIP])
    os.chdir(SOURCEDIR)
    check_call([PYTHON, 'run_tests.py'])
    check_call([PYTHON, 'PYMECAVIDEO.py', '--autosimu'])
    os.chdir('..')
    shutil.rmtree(SOURCEDIR)
    os.chdir(orig_path)
    report('%s tested successfully' % SOURCEDIR_ZIP)


def upload_inst(options):
    target_link = upload_file(
        options, (DIR_RELEASE_DEV + INSTALLER_NAME + '.exe', INSTALLER_NAME + '.exe'))
    replace_release_line(LINE_WIN_EXE, target_link)


def upload_zip(options):
    target_link = upload_file(
        options, (DIR_RELEASE_DEV + PYMECAVIDEO_VER_ZIP, PYMECAVIDEO_VER_ZIP))
    replace_release_line(LINE_WIN_ZIP, target_link)


def upload_src(options):
    target_link = upload_file(
        options, (DIR_RELEASE_DEV + SOURCEDIR_ZIP, SOURCEDIR_ZIP))


URL_FH = 'http://labs.freehackers.org/'


def br_login(br, options):
    report('Fetching labs.freehackers.org/login page...')
    page = br.open(URL_FH + 'login')

    report('Logging in...')
    br.select_form(nr=1)
    br["username"] = "philippe"
    assert options.pwd
    br["password"] = options.pwd
    br["autologin"] = 0
    page = br.submit()
    s = page.read()
    # print (s)
    s.index('Logged in as')


def upload_file(options, fileInfo):
    '''fileInfo should be: (path, name).'''

    filePath, fileName = fileInfo
    assert os.path.exists(filePath)

    br = mechanize.Browser()
    br.set_handle_robots(False)

    br_login(br, options)

    report('Opening PYMECAVIDEO - File list page...')
    page = br.open(URL_FH + 'projects/PYMECAVIDEO/files/')
    s = page.read()
    nb_match_before = s.count(fileName.replace(' ', '_'))
    # print (nb_match_before)
    # print (s)

    report('Opening PYMECAVIDEO - New Files page...')
    page = br.open(URL_FH + 'projects/PYMECAVIDEO/files/new')
    s = page.read()
    # print (s)

    report('Registering the file')
    br.select_form(nr=1)
    control = br.find_control("version_id")
    targetLabel = VersionInfo.longVersion
    # print (control.get_items())
    value = None
    for item in control.get_items():
        for label in item.get_labels():
            if label.text == targetLabel:
                value = item.attrs['value']
                break
    if value == None:
        report('Version unknown on labs.freehackers.org, did you declare it ?')
        sys.exit(0)
    br["version_id"] = [value]

    br.add_file(open(filePath, 'rb'), None, fileName)
    report('Uploading %s' % fileName)
    page = br.submit()
    # print (page.read())
    report('File submitted : %s' % fileName)

    report('Opening PYMECAVIDEO - File list page...')
    page = br.open(URL_FH + 'projects/PYMECAVIDEO/files/')
    s = page.read()
    # print (s)
    fileName = fileName.replace(' ', '_')
    nb_match_after = s.count(fileName)
    # print (nb_match_after)
    assert nb_match_after > nb_match_before

    all_matching_links = list(br.links(text=fileName))
    target_link_info = all_matching_links[-1]
    target_link = URL_FH[:-1] + target_link_info.url
    report('Target: %s' % target_link)
    return target_link


funcList = [make_exe, make_zip_exe, test_zip, make_inst,
            make_zip_src, test_src, upload_inst, upload_zip, upload_src]
funcListName = [f.__name__ for f in funcList]


def main():
    parser = OptionParser(conflict_handler='resolve',
                          add_help_option=True)
    parser.add_options([
        Option('--console', action='store_true', dest='console'),
        Option('--window', action='store_false', dest='console'),
        Option('--pwd', action='store', default=''),
        Option('--debug', action='store_true', default=False, dest='debug'),
        Option('--release', action='store_false', dest='debug'),
        Option('--dev', action='store_true'),
    ])
    options, args = parser.parse_args()

    if len(args) == 0:
        print('Mandatory Argument: ')
        print('\n'.join(funcListName))
        sys.exit(1)
    else:
        for funcName in args:
            if not funcName in funcListName:
                print('Unsupported argument: %s' % funcName)
                print('Possible choices: ' + ' '.join(funcListName))
                sys.exit(1)

    if options.dev:
        hgVersionInfo = Popen(['hg', 'log', '-l1'],
                              stdout=PIPE).communicate()[0]
        hgRevInfo = hgVersionInfo.split()[1]
        hgRev, hgHash = hgRevInfo.split(':')
        VersionInfo.shortVersion = 'r' + hgRev
        VersionInfo.longVersion = 'PYMECAVIDEO %s:%s' % (hgRev, hgHash)

    setglobal()

    for funcName in args:
        for f in funcList:
            if f.__name__ == funcName:
                f(options)
                break
        else:
            print('Unrecognised command:', funcName)


if __name__ == '__main__':
    main()
