#!/usr/local/bin/python

import os, re, sqlite3
from bs4 import BeautifulSoup, NavigableString, Tag 

def gen_db():
    conn = sqlite3.connect('NTAPI.docset/Contents/Resources/docSet.dsidx')
    cur = conn.cursor()

    try: cur.execute('DROP TABLE searchIndex;')
    except: pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    docpath = 'NTAPI.docset/Contents/Resources/Documents'

    for root, dirs, files in os.walk(docpath):
        for f in files:
            if f.endswith(".html"):
                namepart = f.split(".")[0]
                entrytype = 'literal'
                with open(os.path.join(root, f), 'r') as fd:
                    contents = fd.read()
                    soup = BeautifulSoup(contents, features="html.parser")
                    fn = soup.find("pre", class_='FnDefinition')
                    if fn:
                        # print(fn.text)
                        # Check if it's a typedef
                        if 'typedef enum' in fn.text:
                            # print("Enum found: {}".format(fn))
                            entrytype = 'Enum'
                        if 'typedef struct' in fn.text:
                            # print("Struct found: {}".format(fn))
                            entrytype = 'Struct'
                        elif 'NTAPI' in fn.text or 'WINAPI' in fn.text or 'cdecl' in fn.text:
                            # print("Function found: {}".format(fn))
                            entrytype = 'Function'
                        print("Adding {} to index as {}".format(namepart, entrytype))
                        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (namepart, entrytype, f))
                    else:
                        print("Couldn't find FnDefinition for {}, adding as {}".format(namepart, entrytype))
                        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (namepart, entrytype, f))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    gen_db()
