import urllib
from urllib.parse import urljoin
import re
import os
import shutil
from page_getter import PageGetter
from titles import create_tokens
from fix_html import fix_htmls
import sys
from gen_db import gen_db
from bs4 import BeautifulSoup

# documentation for creating docsets for Dash: http://kapeli.com/docsets/


base_url = "https://undocumented.ntinternals.net/"
docset_root = "NTAPI.docset"
root_path = "{}/Contents/Resources/Documents/".format(docset_root)
crawl_path = "download_folder/"
main_page = ""   # MSDN page: "Windows desktop app development"

def crawl():
    page_getter = PageGetter(base_url)
    with open("links.txt") as f:
        lines = list(f)
        urls_to_visit = [x.strip() for x in lines]
    known_urls = set(urls_to_visit)   # URLs we visited or will visit
    visited_count = 0

    while len(urls_to_visit) > 0:
        cur_url = urls_to_visit.pop(0)
        local_url = urllib.parse.unquote(os.path.join(crawl_path, cur_url))
        remote_url = base_url + cur_url
        print("(%d remaining, %d visited)\r" % (len(urls_to_visit), visited_count), end="")
        sys.stdout.flush()
        if not os.path.exists("/".join(local_url.split("/")[:-1])):
            os.makedirs("/".join(local_url.split("/")[:-1]))
        if os.path.exists(local_url):
            cur_url_html = open(local_url, "r").read()
        else:
            cur_url_html = page_getter.urlretrieve(remote_url, local_url)
        visited_count += 1
        soup = BeautifulSoup(cur_url_html, features="html.parser")
        links = soup.find_all("a")
        new_urls = []
        for link in links:
            # print("Before", link)
            if 'href' in link.attrs:
                if not re.match(r"https?:", link['href']):
                    new_urls.append(urljoin(cur_url, link['href']))
        # print(new_urls)
        new_urls = set(url for url in new_urls if url not in known_urls)
        urls_to_visit.extend(new_urls)
        known_urls.update(new_urls)
    print("Done crawling. Crawled {} pages".format(visited_count))

def main():
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    if not os.path.exists(crawl_path):
        os.makedirs(crawl_path)
    crawl()
    fix_htmls()
    create_tokens("{}/Contents/Resources/Tokens.xml".format(docset_root))
    shutil.copy("static/icon16.png", "{}/icon.png".format(docset_root))
    shutil.copy("static/Info.plist", "{}/Contents/".format(docset_root))
    shutil.copy("static/Nodes.xml", "{}/Contents/Resources/".format(docset_root))
    gen_db()

if __name__ == "__main__":
    main()
