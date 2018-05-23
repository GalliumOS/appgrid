# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from appdata import DB_PATH


def update_state(pkgname, state):
    # add deb files to db
    # removing may lead to deletion
    state = '' if state == 'available' else state[0]
    import os.path
    if not os.path.exists(DB_PATH):
        return
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    res = c.execute('select state from apps where pkgname=?',
                    (pkgname.split(':')[0],)).fetchone()
    if res and res[0] != state:
        c.execute('update apps set state=? where pkgname=?',
                  (state, pkgname.split(':')[0],))
        c.execute('update ftable set state=? where pkgname=?',
                  (state, pkgname.split(':')[0],))
        conn.commit()
    conn.close()


def rebuild_db():
    # ratings initialization
    import json
    from appdata.helpers import request
    url = 'https://reviews.ubuntu.com/reviews/api/1.0/review-stats/any/any/'
    ratings = {}
    try:
        j = json.loads(request(url, cache=0) or '[]')
    except:
        j = []
    for subjson in j:
        if subjson['histogram'] and subjson['ratings_average'] != '0.00':
            h = json.loads(subjson['histogram'])
            h = [h[0] + h[1], h[2] + h[3], h[4]]
            q = (h[0] + 2 * h[1] + 3 * h[2]) / sum(h)
            if q < 1.66:
                r = 1
            elif q < 2.33:
                r = 2
            else:
                r = 3
            ratings[subjson['package_name']] = (r, h[2] - h[0])

    # data
    from appdata.apps.aptapp import AptApp, get_apt_pkgnames, get_desktop_files
    desktop_files = get_desktop_files()

    # order by rating
    p = set()
    s = set()
    for pkgname in get_apt_pkgnames():
        try:
            p.add((ratings[pkgname][1], pkgname))
        except:
            s.add(pkgname)
    p = sorted(p, reverse=True)
    p = [a[1] for a in p]
    s = sorted(s)
    rows = []
    for pkgname in p + s:
        if pkgname in desktop_files:
            app = AptApp(pkgname, desktop=desktop_files[pkgname])
            typ = 'A'
        else:
            app = AptApp(pkgname)
            typ = ''

        try:
            r = ratings[pkgname]
        except:
            r = (0, 0)

        try:
            rows.append((
                ';'.join(app.addons),
                app.category,
                app.description,
                ';'.join(app.keywords),
                app.name,
                app.origin_id,
                app.id,
                r[0],  # rating
                'i' if app.state == 'installed' else '',
                app.summary,
                'A' if typ else '',  # type: internal use 'A' if app, else pkg
                ';'.join(app.version),
                app.website,
            ))
        except:
            pass

    # db
    import os
    if not os.path.exists('/var/cache/appgrid/'):
        os.mkdir('/var/cache/appgrid/')
    from random import choice
    r = ''.join([choice('abcdefghijklmnopqrstuvwxyz') for i in range(10)])
    rpath = DB_PATH + '.' + r + '.tmp'
    if os.path.exists(rpath):
        os.remove(rpath)
    import sqlite3
    conn = sqlite3.connect(rpath)
    c = conn.cursor()

    c.execute('''create table apps(
        addons text,
        category text,
        description text,
        keywords text,
        name text,
        origin text,
        pkgname text primary key,
        rating int,
        state text,
        summary text,
        type text,
        version text,
        website text);''')

    c.execute("create virtual table ftable using fts4(content='apps',"
              "tokenize=simple, matchinfo=fts3, name, summary, keywords,"
              "pkgname, state, category);")

    c.executemany('insert into apps values(?,?,?,?,?,?,?,?,?,?,?,?,?)', rows)
    c.execute("insert into ftable(ftable) values('rebuild');")
    conn.commit()

    # store
    os.rename(rpath, DB_PATH)

    # clean
    for path in os.listdir('/var/cache/appgrid/'):
        if path.endswith('.db'):
            curr_v = int(''.join(c for c in DB_PATH if c.isdigit()))
            this_v = int(''.join(c for c in path if c.isdigit()))
            if this_v < curr_v:
                os.remove('/var/cache/appgrid/' + path)
        elif path.endswith('.tmp'):
            from time import time as t
            if t() - os.path.getmtime('/var/cache/appgrid/' + path) > 600:
                os.remove('/var/cache/appgrid/' + path)


if __name__ == '__main__':
    from argparse import ArgumentParser

    ap = ArgumentParser()
    ap.add_argument('--rebuild', action='store_true', help="rebuild db")
    ap.add_argument('--update_state', help="preselect search term")
#    ap.add_argument('request', help="package name or path to deb file",
#                    nargs='?')

    args = vars(ap.parse_args())

    if args['rebuild']:
        rebuild_db()
    if args['update_state']:
        update_state(args['update_state'].split(';')[1],
                     args['update_state'].split(';')[0])
