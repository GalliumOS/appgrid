# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file


def get_client(request, force=False):
    import sqlite3
    from appdata import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    row = conn.cursor().execute("select * from apps where pkgname=? limit 1",
                                (request,)).fetchone()
    conn.close()
    if row:
        from appdata.apps.sqliteapp import SQLiteApp
        return SQLiteApp(row)
    import os.path
    from mimetypes import guess_type
    if (os.path.exists(request) and
            guess_type(request)[0] == 'application/x-debian-package'):
        from appdata.apps.debfileapp import DebFileApp
        return DebFileApp(request)
    import subprocess
    o = subprocess.check_output(["apt-cache", "policy", request],
                                stderr=subprocess.STDOUT).decode('utf8')
    if o.count('\n') > 4 and not (o.split('\n')[1].endswith(')') and
                                  o.split('\n')[2].endswith(')')):
        fline = o.split('\n')[0]
        if fline.endswith(':') and fline.startswith(request + ':'):
            # upgrade to multiarch package name (eg steam)
            request = fline.rsplit(':', 1)[0]
        from appdata.apps.aptapp import AptApp
        return AptApp(request, force=force)
    return None


def get_clients(category='',  # 'Arts', 'Arts;Graphics'
                search='',
                sort='',  # 'rating'
                state='',  # 'installed'
                offset=0,
                ):  # rating?, max_results?
    import sqlite3
    from appdata import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    args = []

    # form query
    rr = False
    if search or category or state:
        query = ('select apps.pkgname, apps.name, apps.description, '
                 'apps.rating, apps.state from '
                 'ftable join apps using(pkgname) where ftable match ?')
        tmp = []
        if category:
            tmp.append('category:' + category)
        if search:
            tmp.append('(pkgname:' + search.replace('-', ' ') + '*' +
                       ' OR name:' + search.replace('-', ' ') + '*)')
        if state:
            tmp.append('state:i')
        args = [' '.join(tmp)]
    elif sort:
        query = 'select pkgname, name, description, rating, state from apps'
    else:
        query = ("select pkgname, name, description, rating"
                 ", state from apps where type!='' and random() % 15 = 0")
        rr = True

    # all queries minus natural sorted search
    if sort or not search:
        rows = c.execute('%s limit 100 offset ?;' % query,
                         tuple(args + [offset])).fetchall()
        conn.close()
        return rows + ['more?'] if rr or len(rows) == 100 else rows

    # search (matches pkgname or name)
    rows = c.execute('%s limit 100;' % query, tuple(args)).fetchall()
    if len(rows) == 100:
        conn.close()
        return rows[offset:]

    # top up search (matches summary or keywords)
    arg = args[0].replace('pkgname:', 'summary:').replace('name:', 'keywords:')
    pkgnames = [r[0] for r in rows]
    rows += [r for r in c.execute('%s limit 100;' % query, (arg,)
                                  ).fetchall() if not r[0] in pkgnames]
    conn.close()
    return rows[offset:]
