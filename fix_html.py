import re
import os
import shutil
import urllib
import sys
from page_getter import PageGetter
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose

css_dict = {}
css_count = 0
empty_count = 0

def fix_css(soup, path):
    """ Update CSS reference in an HTML code; download the css if it doesn't exist locally """
    from main import crawl_path, root_path, base_url
    global css_count
    global css_dict
    global empty_count

    css_found = soup.find_all("link", rel="stylesheet")

    if len(css_found) == 0:
        empty_count += 1

    page_getter = PageGetter(base_url)
    for css_lnk in css_found:
        if 'href' in css_lnk.attrs:
            if css_lnk['href'] not in css_dict.keys():
                local_file = "css_{}.css".format(css_count)
                css_count += 1
                full_url = urllib.parse.urljoin("/".join([base_url, "/".join(path.split("/")[1:])]), css_lnk['href'])
                print("\n", full_url)
                css_data = page_getter.urlretrieve(full_url, os.path.join(root_path, local_file))
                css_dict[css_lnk['href']] = local_file
                css_lnk['href'] = local_file
                print(css_lnk)
            else:
                # Replace existing ones
                css_lnk['href'] = css_dict[css_lnk['href']]

    return soup

def fix_html(path):
    from main import crawl_path, root_path, base_url
    print("Path:", path)
    page_data = open(path, "r").read()
    # fix links
    page_data = page_data.replace(base_url, "")
    # add content encoding for browser
    page_data = page_data.replace("<head>", """<head>\n<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">\n""")
    # Remove redirect
    page_data = re.sub("<script.*?</script>", "", page_data, flags=re.DOTALL)
    # remove header
    page_data = re.sub('<div id="ux-header".*?<div id="breadcrumbs"', '<div id="breadcrumbs"', page_data, flags=re.DOTALL)
    # remove footer
    page_data = re.sub('<div id="standardRatingBefore".*?<span class="logoLegal">', '<footer class="bottom" role="contentinfo"><span class="logoLegal">', page_data, flags=re.DOTALL)
    # remove breadcrumb button
    page_data = re.sub('class="breadcrumbDropSmall"', "", page_data, flags=re.DOTALL)
    page_data = re.sub(' role="button" aria-expanded="false"', "", page_data, flags=re.DOTALL)
    page_data = re.sub('href="#" target', "", page_data, flags=re.DOTALL)
    # remove TOC slider button
    page_data = re.sub("""<a id="tocMenuToggler".*?</a>""", "", page_data, flags=re.DOTALL)
    # make TOC expanded by default
    page_data = re.sub("""<span id="tocExpandButton".*?</span>""", "", page_data, flags=re.DOTALL)
    page_data = re.sub(""" id="tocExpand">""", "", page_data, flags=re.DOTALL)
    # remove floating right navigation menu (print, export, share...)
    page_data = re.sub("""<div id="rightNavigationMenu".*?<ul id="indoc_toclist"></ul>\s*</div>\s*</div>\s*</div>""", "", page_data, flags=re.DOTALL)
    # remove "topic not in scope" notification
    page_data = re.sub("""<div class="topicNotInScope" id="topicNotInScope">.*?<div class="Clear"></div>\s*</div>\s*</div>""", "", page_data, flags=re.DOTALL)
    # remove "Other Versions" dropbox
    page_data = re.sub("""<div class="lw_vs">.*?<div style="clear:both;">""", '<div style="clear:both;">', page_data, flags=re.DOTALL)
    # remove "not being maintained" messages
    page_data = re.sub("""<div id="archiveDisclaimer">.*not being maintained.</div>""", "", page_data, flags=re.DOTALL)
    # Parse with BS
    soup = BeautifulSoup(page_data, features="html.parser")
    links = soup.find_all("a")
    for link in links:
        # print("Before", link)
        if 'href' in link.attrs:
            href_path = link['href'].split("/")
            link['href'] = href_path[-1]

    soup = fix_css(soup, path)

    # Make sure the new docset dir exists
    lead_path = os.path.join(root_path, *os.path.split(path)[1:-1])
    dest_path = os.path.join(lead_path, os.path.split(path)[-1])
    if not os.path.exists(lead_path):
        # print("Creating {}".format(lead_path))
        os.makedirs(lead_path)
    print("Creating {}".format(dest_path))
    # import pdb; pdb.set_trace()
    # Remove bad nbsp
    finalpage_data = str(soup).replace('\xa0','')
    open(dest_path, "w").write(finalpage_data)
    # open(path, "w").write(soup.prettify())

def fix_htmls():
    from main import crawl_path, root_path, main_page
    # files_to_fix = os.listdir(crawl_path)
    files_to_fix = []
    for root, dirs, files in os.walk(crawl_path):
        for name in files:
            if name.endswith('.html'):
                files_to_fix.append(os.path.join(root, name))
    total = len(files_to_fix)
    precent = int(total / 100)
    current = 0
    print("Patching HTML files")
    for path in files_to_fix:
        print("Fixing {}".format(path))
        fix_html(path)
        if precent != 0 and current % precent == 0:
            percent_txt = float(current) / float(total) * 100.0
            print("%d%% (downloaded %d css files; %d files have no css link)\r" % (percent_txt, css_count, empty_count), end="")
            sys.stdout.flush()
        current += 1
    # Copy index page
    shutil.copy(os.path.join(root_path, "title.html"), os.path.join(root_path, "index.html"))
    print("\r100%% (downloaded %d css files; %d files have no css link)" % (css_count, empty_count))

if __name__ == "__main__":
    fix_htmls()
