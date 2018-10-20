import glob
import re
import os
from collections import Counter

token_entry_template = """<File path="docs/{}">
  <Token><TokenIdentifier>//apple_ref/cpp/{}/{}</TokenIdentifier></Token>
</File>"""

# https://kapeli.com/docsets#supportedentrytypes
title_dict = {
    "api": "Interface",
    "attribute": "Attribute",
    "class": "Class",
    "component": "Component",
    "constants": "Constant",
    "constructor": "Constructor",
    "element": "Element",
    "enumeration": "Enum",
    "event": "Event",
    "example": "Sample",
    "field": "Field",
    "file": "File",
    "function": "Function",
    "interface": "Interface",
    "macro": "Macro",
    "member": "Variable",
    "message": "Event",
    "method": "Method",
    "object": "Object",
    "overview": "Category",
    "property": "Property",
    "provider": "Provider",
    "reference": "Category",
    "resource": "Resource",
    "routine": "Subroutine",
    "sample": "Sample",
    "service": "Service",
    "structure": "Struct",
    "test": "Test",
    "type": "Type",
    "union": "Union",

    "attributes": "Category",
    "classes": "Category",
    "components": "Category",
    "constructors": "Category",
    "elements": "Category",
    "enumerations": "Category",
    "events": "Category",
    "examples": "Category",
    "files": "Category",
    "functions": "Category",
    "interfaces": "Category",
    "macros": "Category",
    "members": "Category",
    "methods": "Category",
    "objects": "Category",
    "properties": "Category",
    "references": "Category",
    "resources": "Category",
    "routines": "Category",
    "samples": "Category",
    "services": "Category",
    "structures": "Category",
    "tests": "Category",
    "types": "Category",
    "values": "Category",
}

def create_tokens(out_path):
    from main import root_path
    print("Creating token file")
    out_file = open(out_path, "w")
    out_file.write('<Tokens version="1.0">')

    fs = []
    for root, dirs, files in os.walk(root_path):
        for name in files:
            if name.endswith('.html'):
                print(name)
                fs.append(os.path.join(root, name))
    titles = Counter()
    referenced = 0
    for f in fs:
        print(f)
        d = open(f, "r").read()
        try:
            title = re.search('<title>([^\[(<]*)', d, re.DOTALL).group(1)
            assert title.strip()
        except:
            print("Failed to parse title:", f)
            continue

        title = title.strip()
        if title[0].isdigit():
            continue
        title_type = title.lower().split()[-1]
        title_name = title.rsplit(' ', 1)[0]
        if title_type in title_dict.keys():
            file_path = os.path.basename(f)
            obj_type = title_dict[title_type]
            if title.lower().startswith("about"):
                obj_type = "Category"
            if obj_type in ["Category", "Interface"]:
                title_name = title
            out_file.write(token_entry_template.format(file_path, obj_type, title_name)+'\n')
            referenced += 1

        titles.update([title_type])

    out_file.write('</Tokens>\n')

    print("%d added to token" % referenced)
    print("Top Titles:")
    for title, count in titles.most_common(40):
        print('\t', title, count)

if __name__ == "__main__":
    create_tokens("NTAPI.docset/Contents/Resources/Tokens.xml")
