"""
Currently, Prerender injects 1000s of lines of CSS into each file. Shrink utility replaces this with a CSS
link to a file of all the stuff that was once there.

This script renews the consolidated CSS file with the stuff the OSF pages of tomorrow have injected into them.
"""
from bs4 import BeautifulSoup
import requests

# Reading from HTTP request vs. from a file
REMOTE = True

# URLs to use if REMOTE. Any example of each type of page will do, really
page_urls = {
    'https://osf.io/2ngdw/files': 'Project Files',
    'https://osf.io/2ngdw/wiki': 'Project Wiki',
    'https://osf.io/2ngdw/analytics': 'Project Analytics',
    'https://osf.io/2ngdw/forks': 'Project Forks',
    'https://osf.io/2ngdw/registrations': 'Project Registrations',
    'https://osf.io/c7vbx': 'User',
    'https://osf.io/institutions/cos': 'Institution'
}

# Local filename if not REMOTE
FILENAME = ''
# Remove style element from the local file after scraping
SHRINK_FILE = True

# Output CSS file
CSS_FILEPATH = '../archive/static/consolidated.css'


giblets = []
css = open(CSS_FILEPATH, 'w')


# Remove style tags and put the content in the consolidated file
def scrape_css(html, css_file):

    soup = BeautifulSoup(html, 'html.parser')

    for elem in soup.findAll('style'):
        giblet = elem.text
        if giblet not in giblets:
            giblets.append(elem.text)
        elem.extract()

    link_tag = soup.new_tag("link", href=CSS_FILEPATH, rel="stylesheet")
    if soup.head is not None:
        soup.head.insert(0, link_tag)

    return str(soup)


# Use a website as a base to copy CSS
def stream_html(url):
    header = {
        "User-agent": "LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)"}

    html = requests.Session().get(url, headers=header).text
    scrape_css(html, css)


# Use a file to copy CSS and remove it from the file
def open_html(path):
    file = open(path, 'r+')
    new_html = scrape_css(file, css)

    if SHRINK_FILE:
        file.seek(0)
        file.write(new_html)
        file.truncate()

    file.close()


def main():

    if REMOTE:
        # Go through every page type
        for page in page_urls:
            print("Extracting", page_urls[page], page)
            stream_html(page)

    else:
        open_html(FILENAME)

    for block in giblets:
        css.write(block + '\n')

    css.close()

if __name__ == '__main__':
    main()
