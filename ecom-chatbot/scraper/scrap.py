from collections import deque
from html.parser import HTMLParser
from dotenv import load_dotenv

import requests
import re
import urllib.request
import os

from urllib.parse import urlparse

load_dotenv()

URL_PATTERN = r'^https://www\.saatva\.com/(mattresses|furniture|bedding)/$'

openai_api_key = os.getenv('OPENAI_API_KEY')

domain_url = "https://www.saatva.com"

# Parse html and extract all links
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])


# Get all hyperlinks from a URL
def get_links(url):
    try:
        with urllib.request.urlopen(url) as response:
            if not response.info().get('Content-Type').startswith('text/html'):
                return []
            html = response.read().decode('utf-8')
    except Exception as e:
        print(e)
        return []
    
    parser = LinkParser()
    parser.feed(html)
    return parser.links


# get hyperlinks from a URL that are from the same domain
def get_domain_link(local_domain, url):
    clean_links = []
    for link in set(get_links(url)):
        clean_link = None

        # Skipping the primary domain
        if link == "https://" + local_domain or link == "https://" + local_domain + "/":
            continue

        if re.match(URL_PATTERN, link):
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link
        else:
            if link.startswith("/"):
                clean_link = "https://" + local_domain + link
        
        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    return list(set(clean_links))


def scrap(url):
    local_domain = urlparse(url).netloc

    queue = deque([url])

    seen = set([url])

    if not os.path.exists("data/"):
        os.mkdir("data/")

    if not os.path.exists("data/"+local_domain+"/"):
        os.mkdir("data/" + local_domain + "/")

    # While the queue is not empty, continue crawling
    while queue:

        url = queue.pop()
        
        # Try extracting the text from the link, if failed proceed with the next item in the queue
        try:
            with open('data/'+local_domain+'/'+url[8:].replace("/", "_") + ".txt", "w", encoding="UTF-8") as f:
                response = requests.get(url)
                response_as_string = str(response.content)  # Convert the entire Response object's content to a string
                clean_html_content = re.sub(r'<.*?>|function|let|var|return|for|while|if|else|document|window|class|style|[^\w\s.,!?;]', ' ', response_as_string)
                clean_html = re.sub(r'<.*?>', ' ', clean_html_content)
                js_keywords = r'\b(function|let|var|const|return|for|while|do|switch|case|break|continue|if|else|true|false|null|undefined)\b'
                clean_js = re.sub(js_keywords, ' ', clean_html)
                css_keywords = r'\b(style|color|background|border|margin|padding|font)\b'
                clean_css = re.sub(css_keywords, ' ', clean_js)
                clean_special_chars = re.sub(r'[^\w\s.,!?;]', ' ', clean_css)

                text = str("WEBPAGE: "+ str(url)+ "\n")
                text = text + clean_special_chars

                if ("You need to enable JavaScript to run this app." in text):
                    print("Unable to parse page " + url + " due to JavaScript being required")
            
                f.write(text)
        except Exception as e:
            print("Unable to parse page " + url)
            print(e)

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_link(local_domain, url):
            if link not in seen:
                queue.append(link)
                seen.add(link)          

if __name__ == "__main__":
    scrap(domain_url)





