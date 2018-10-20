ntapi_docset
===========

docset for Zeal or Dash containing the [Undocumented NTAPI Reference](https://undocumented.ntinternals.net/)

### Requirements

* BeautifulSoup 4
* pysqlite3
* Python 3.6 or higher

### Build

To build, run the following command:

```shell
> python main.py
```

This will crawl all the links in links.txt, and resolve all the hyperlinks as it goes. This currently results in a little more than 1200 requests. It will download all the HTML, fix it up, get all the CSS, and create the structure for the docset.

### Install

Install by putting in your Zeal docset folder and starting the viewer.