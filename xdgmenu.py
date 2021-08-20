#!/usr/bin/env python3

import os
import glob
import re
from collections import OrderedDict
import xdg.DesktopEntry as dentry
import xdg.Exceptions as exc
import xdg.BaseDirectory as bd


def remove_keys(cmd, desktopfile):
    '''
    Some KDE apps have this -caption %c in a few variations. %c is The
    translated name of the application as listed in the appropriate Name key in
    the desktop entry.

    The location of the desktop file as either a URI (if for example gotten
    from the vfolder system) or a local filename or empty if no location is
    known.

    Removing any remaining keys and trailing options from the command.
    '''
    cmd = cmd.replace('-caption "%c"', '')
    cmd = cmd.replace("-caption '%c'", '')
    cmd = cmd.replace('-caption %c', '')
    cmd = cmd.replace('"%k"', desktopfile)
    cmd = cmd.replace("'%k'", desktopfile)
    cmd = cmd.replace('%k', desktopfile)
    cmd = cmd.partition(' %')[0]
    return cmd


def get_terminal():
    '''
    Dictionaries are insertion ordered as of 3.6+
    https://stackoverflow.com/a/39980744
    '''
    paths = {
        '/usr/bin/x-terminal-emulator': '-e',
        '/usr/bin/xfce4-terminal': '-x',
        '/usr/bin/gnome-terminal': '-x',
        '/usr/bin/mate-terminal': '-x',
        '/usr/bin/lxterminal': '-x',
        '/usr/bin/konsole': '-x',
        '/usr/bin/stterm': '-e',
        '/usr/bin/uxterm': '-e',
        '/usr/bin/urxvt': '-e',
        '/usr/bin/xterm': '-e',
    }
    for path, opt in paths.items():
        if os.path.exists(path):
            return path + ' ' + opt


def get_category(categories):
    main_categories = [
        'AudioVideo',
        'Audio',
        'Video',
        'Development',
        'Education',
        'Game',
        'Graphics',
        'Network',
        'Office',
        'Science',
        'Settings',
        'System',
        'Utility',
    ]

    for c in categories:
        if c in main_categories:
            if re.match('Audio|Video', c):
                return 'Multimedia'
            else:
                return c
    return 'Other'


def get_desktop_info(desktopfile):
    de = dentry.DesktopEntry(filename=desktopfile)

    # skip processing the entry if any of these attributes are set.
    only = de.getOnlyShowIn()
    hidden = de.getHidden()
    nodisplay = de.getNoDisplay()
    if (only != []) or hidden or nodisplay:
        return None

    name = de.getName().encode('utf-8')
    name = name.decode()
    cmd = de.getExec()
    cmd = remove_keys(cmd, desktopfile)

    terminal = get_terminal()
    run_in_terminal = de.getTerminal()
    if run_in_terminal:
        cmd = f'{terminal} {cmd}'

    categories = de.getCategories()
    category = get_category(categories)

    return name, cmd, category


def get_desktop_files():
    # some directories are mentioned twice in bd.xdg_data_dirs, once
    # with and once without a trailing /
    dirs = set([d.rstrip('/') for d in bd.xdg_data_dirs])
    filelist = []

    for d in dirs:
        files = glob.glob(os.path.join(d, 'applications/*.desktop'))
        for f in files:
            filelist.append(f)

    return filelist


def menu():
    catlist = []
    appdict = {}

    for desktopfile in get_desktop_files():
        try:
            name, cmd, category = get_desktop_info(desktopfile)
            if name is not None:
                catlist.append(category)
                appdict[name] = cmd, category
        except exc.ParsingError:
            pass
        except TypeError:
            pass

    appdict = OrderedDict(sorted(appdict.items(), key=lambda x: x[0].lower()))
    catdict = {}

    for c in sorted(catlist):
        catapps = {}
        for name, cmd in appdict.items():
            if cmd[1] == c:
                catapps[name] = cmd[0]
        catdict[c] = catapps

    return catdict


def main():
    for cat, apps in menu().items():
        print(f'{cat}')
        for name, cmd in apps.items():
            print(f'\t{name} = {cmd}')


if __name__ == "__main__":
    main()
