# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file


def get_cat_for_app(categories):
    categories = categories.split(';')
    for key in category_subcat:
        if key in categories:
            return category_subcat[key]
    for key in category_cat:
        if key in categories:
            return category_cat[key]
    return 'System'


def get_cat_for_pkg(section, pkgname):
    if '-' in pkgname:
        pp = pkgname.split('-')
        if pp[0] == 'python':
            return 'Programming;Python'
        elif pp[0] in ['fonts', 'ttf', 'otf']:
            return 'System;Fonts'
        elif pp[-1] in ['backgrounds', 'wallpapers', 'theme']:
            return 'System;Appearance'
    try:
        return section_cat[section]
    except:
        return 'System'


# category data
# this means that categories will be untranslated, but still extracted for i18n
def _(text):
    return text


categories = {
    _('Programming'): [_('Haskell'), _('Java'), _('Libraries'), _('Mono/CLI'),
                       _('OCaml'), _('Perl'), _('Python'), _('Ruby'),
                       _('Web Development')],
    _('Arts'): [_('Graphics'), _('Languages'), _('Multimedia')],
    _('Games'): [_('Arcade'), _('Board Games'), _('Card Games'), _('Puzzles'),
                 _('Role-Playing'), _('Simulation')],
    _('Productivity'): [_('Communication'), _('Text Editors'),
                        _('Web Browsers')],
    _('Sciences'): [_('Natural Sciences'), _('Engineering'), _('Mathematics')],
    _('System'): [_('Accessibility'), _('Appearance'), _('Configuration'),
                  _('Documentation'), _('Fonts'), _('Language Support')],
}


# mappings to determine the category of a given package
# http://standards.freedesktop.org/menu-spec/latest/apa.html

category_cat = {
    'AudioVideo': 'Arts;Multimedia',
    'Audio': 'Arts;Multimedia',
    'Video': 'Arts;Multimedia',
    'Development': 'Programming',
    # 'Education': 'Education',
    'Game': 'Games',
    'Graphics': 'Arts;Graphics',
    'Network': 'System;Configuration',
    'Office': 'Productivity',
    'Settings': 'System',
    'System': 'System',
    'Utility': 'System',
    'Profiling': 'Programming',
    'Calandar': 'Productivity',
    'ContactManagement': 'Productivity',
    # Database ??
    'Dictionary': 'Productivity',
    'Chart': 'Productivity',
    'Finance': 'Productivity',
    'FlowChart': 'Productivity',
    'PDA': 'Productivity',
    'ProjectManagement': 'Productivity',
    'Presentation': 'Productivity',
    'Spreadsheet': 'Productivity',
    'WordProcessor': 'Productivity;Text Editors',
    '2DGraphics': 'Arts;Graphics',
    'TextTools': 'System',  # ??
    'Printing': 'System',
    'PackageManager': 'System',
    'Dialup': 'System',
    'News': 'Productivity',
    'RemoteAccess': 'System',
    'Telephony': 'Productivity;Communication',
    'TelephonyTools': 'Productivity;Communication',
    'VideoConference': 'Productivity;Communication',
    'MIDI': 'Arts;Multimedia',
    'Mixer': 'Arts;Multimedia',
    'Sequencer': 'Arts;Multimedia',
    'Tuner': 'Arts;Multimedia',
    'TV': 'Arts;Multimedia',
    'AudioVideoEditing': 'Arts;Multimedia',
    'Player': 'Arts;Multimedia',
    'Recorder': 'Arts;Multimedia',
    'DiscBurning': 'System',
    'ActionGame': 'Games',
    'AdventureGame': 'Games',
    'KidsGame': 'Games',
    'LogicGame': 'Games;Puzzles',
    'StrategyGame': 'Games',
    'Art': 'Arts;Graphics',
    # Contruction ??
    'Music': 'Arts;Multimedia',
    'Languages': 'Arts;Languages',
    'Science': 'Sciences',
    'ArtificialIntelligence': 'Sciences',
    'Economy': 'Productivity',
    'History': 'Arts',
    'ImageProcessing': 'Priductivity',
    'Literature': 'Arts;Languages',
    'ParallelComputing': 'Programming',
    # Amusement ??
    'Archiving': 'System',
    'Compression': 'System',
    'Emulator': 'System',
    'FileTools': 'System',
    'FileManager': 'System',
    'TerminalEmulator': 'System',
    'Filesystem': 'System',
    'Monitor': 'System',
    'Security': 'System',
    'Calculator': 'Productivity',
    'Clock': 'Productivity',
    'TextEditor': 'Productivity;Text Editors',
}

category_subcat = {
    'Building': 'Programming',
    'Debugger': 'Programming',
    'IDE': 'Programming',
    'GUIDesigner': 'Programming',
    'RevisionControl': 'Programming',
    'Translation': 'Programming;Localization',
    'Email': 'Productivity;Communication',
    'VectorGraphics': 'Arts;Graphics',
    'RasterGraphics': 'Arts;Graphics',
    '3DGraphics': 'Arts;Graphics',
    'Scanning': 'Productivity',
    'OCR': 'Productivity',
    'Photography': 'Arts;Graphics',
    'Publishing': 'Productivity',
    'Viewer': 'Productivity',
    'DesktopSettings': 'System;Configuration',
    'HardwareSettings': 'System;Configuration',
    'InstantMessaging': 'Productivity;Communication',
    'Chat': 'Productivity;Communication',
    'IRCClient': 'Productivity;Communication',
    'FileTransfer': 'Productivity',
    'HamRadio': 'Sciences;Engineering',
    'P2P': 'Productivity',
    'WebBrowser': 'Productivity;Web Browsers',
    'WebDevelopment': 'Programming;Web Development',
    'ArcadeGame': 'Games;Arcade',
    'BoardGame': 'Games;Board Games',
    'CardGame': 'Games;Card Games',
    'CardGame': 'Games;Card Games',
    'RolePlaying': 'Games;Role-Playing',
    'Simulation': 'Games;Simulation',
    'SportsGame': 'Games;Simulation',
    'Astronomy': 'Sciences;Natural Sciences',
    'Biology': 'Sciences;Natural Sciences',
    'Chemistry': 'Sciences;Natural Sciences',
    'ComputerScience': 'Sciences;Engineering',
    'DataVisualization': 'Sciences;Mathematics',
    'Electricity': 'Sciences;Engineering',
    'Geography': 'Sciences;Natural Sciences',
    'Geology': 'Sciences;Natural Sciences',
    'Geoscience': 'Sciences;Natural Sciences',
    'Math': 'Sciences;Mathematics',
    'NumericalAnalysis': 'Sciences;Mathematics',
    'MedicalSoftware': 'Sciences;Natural Sciences',
    'Physics': 'Sciences;Natural Sciences',
    'Robotics': 'Sciences;Engineering',
    'Sports': 'Sciences;Natural Sciences',
    'Electronics': 'Sciences;Engineering',
    'Engineering': 'Sciences;Engineering',
    'Accessibility': 'System;Accessibility',
    'Documentation': 'System;Documentation',
}

# see http://packages.ubuntu.com/precise/

section_cat = {
    'admin': 'System',
    'comm': 'System',
    'database': 'Programming',  # more specific
    'devel': 'Programming',
    'editors': 'Productivity;Text Editors',  # specific
    'embedded': 'System',
    'games': 'Games',
    'gnome': 'System',
    'gnustep': 'System',  # ??
    'graphics': 'Arts;Graphics',
    'interpreters': 'Programming',
    'kde': 'System',
    'kernel': 'System',
    'libs': 'System',
    'misc': 'System',
    'net': 'System',
    'news': 'Productivity',
    'oldlibs': 'System',
    'otherosfs': 'System',
    'science': 'Sciences',
    'shells': 'System',
    'sound': 'Arts;Multimedia',  # or system..
    'tex': 'Productivity;Text Editors',
    'text': 'Productivity;Text Editors',
    'utils': 'System',
    'video': 'Arts;Multimedia',  # or system..
    'virtual': 'System',
    'web': 'Productivity',
    'x11': 'System',
    'xfce': 'System',
    'zope': 'Productivity',  # ??
    'cli-mono': 'Programming;Mono/CLI',
    'debug': 'Programming;Libraries',  # meh
    'doc': 'System;Documentation',  # split out dev docs somehow
    'electronics': 'Sciences;Engineering',
    'fonts': 'System;Fonts',
    'gnu-r': 'Sciences;Mathematics',  # not really maths? more programming
    'hamradio': 'Sciences;Engineering',
    'haskell': 'Programming;Haskell',
    'httpd': 'Programming;Web Development',
    'java': 'Programming;Java',
    'libdevel': 'Programming;Libraries',
    'lisp': 'Programming',
    'localization': 'System;Language Support',
    'mail': 'Productivity;Communication',
    'math': 'Sciences;Mathematics',
    'ocaml': 'Programming;OCaml',
    'perl': 'Programming;Perl',
    'php': 'Programming;Web Development',
    'python': 'Programming;Python',
    'ruby': 'Programming;Ruby',
    'translations': 'System;Language Support',
    'vcs': 'Programming',
}
