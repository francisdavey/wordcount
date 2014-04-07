import sys
import re
import argparse
import urllib2
import HTMLParser
import operator
import urlparse
import robotparser

from HTMLParser import HTMLParser
from collections import Counter

BADTAGS=['script', 'style']

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.started=True
        self.bad=False
        self.text=[]
        self.urls=[]
        #self.home_site=home_site
    
    def handle_starttag(self, tag, attrs):
        #self.started=True
        #self.bad=False
        if tag in BADTAGS:
            self.bad=True # need to fix this for nested bad tags
        if tag=="a":
            for (key, value) in attrs:
                if key=="href":
                    components=urlparse.urlparse(value)
                    if re.match("https?", components.scheme):
                        #print(components.path)
                        self.urls.append(value)
                        #print(value)
            #print(attrs)
            

    def handle_endtag(self,tag):
        if tag in BADTAGS:
            self.bad=False

    def handle_data(self, data):
        if not self.bad:
            s=data.strip()
            if len(s) > 0:
                self.text.append(s)
#                for m in re.finditer("\w+", s):
#                    add_count(self.d, m.group(0))

def add_count(d, w):
    w=w.lower()
    if d.has_key(w):
        d[w]=d[w]+1
    else:
        d[w]=1

def main(arglist):
    parser = argparse.ArgumentParser(description="Systematically count incidences of words on a website.")
    parser.add_argument('url')
    args=parser.parse_args()
    home=args.url
    sorted_d=crawl_site(home)
    for (key, value) in sorted_d:
        pass
        print(key, value)


def crawl_site(home, depth=5):
    home_site=urlparse.urlparse(home).netloc
    robots_url=urlparse.urljoin(home, "robots.txt")
    rp=robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    found=[]
    found.append(home)
    d=Counter({})
    #crawl(home, found, home_site, rp, d, depth)
    for result in crawler(home, found, home_site, rp, depth=2):
        #print(result, type(result))
        (depth, url, text_list, urls)=result
        #print(depth, url, urls)
        components=urlparse.urlparse(url)
        print("main loop:", depth, url, notext_link(components))
    sorted_d=sorted(d.iteritems(), key=operator.itemgetter(1))
    #print(found)
    return(sorted_d)

    

def notext_link(components):
    '''Returns true if a link is to a page which should be crawled but should not
    have its text extracted.'''

    return not re.match(".*archive\.html$", components.path)

def bad_link(components):
    return re.match(".*(search|feeds?)", components.path) is not None

def foreign_link(components, home_site):
    return not components.netloc==home_site

def crawler(url, found, home_site, rp, depth=5):
    #print("crawler called: {}".format(url))
    if depth != 0 and rp.can_fetch("*", url):
        try:
            page=urllib2.urlopen(url)
            html=page.read()
            parser=MyHTMLParser()
            parser.feed(html)
            #print("Yielding {} {}".format(depth, url))
            yield(depth, url, parser.text, parser.urls)
            #print(depth, url, parser.text, parser.urls)
            for u in parser.urls:
                components=urlparse.urlparse(u)
                #print(u, home_site, u in found, bad_link(components), foreign_link(components,  home_site))
                #if not (u in found or bad_link(components) or foreign_link(components, home_site)):
                if not foreign_link(components, home_site):
                    found.append(u)
                    #print("Crawling to {}".format(u))
                    for result in crawler(u, found, home_site, rp, depth=depth-1):
                        yield result
        except urllib2.HTTPError as E:
            print(url, E.reason)
            yield (depth, url, None, None)
                
        

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#def crawl(url, found, home_site, rp, D, depth=5):
#    #print(url, depth, found, D)
#    #print(url, depth, len(D), len(found))
#    if depth==0:
#        return None
#    #depth=depth-1
#
#    if rp.can_fetch("*", url):
#        page=urllib2.urlopen(url)
#    html=page.read()
#    parser=MyHTMLParser()
#    parser.bad=False
#    parser.text=[]
#    parser.d=Counter({})
#    parser.home_site=home_site
#    parser.urls=[]
#    parser.feed(html)
#    #print(D == parser.d)
#    #print(len(D), len(parser.d))
#    C=D + parser.d
#    D.update(C)
#    #print(len(D), len(parser.d))
#    for test_url in parser.urls:
#        #print("test_url:", test_url)
#        if test_url[-1]=="/":
#            sub_url=test_url[:-1]
#        else:
#            sub_url=test_url
#        if sub_url in found:
#            continue
#        found.append(sub_url)
#        if re.match(".*archive\.html$", sub_url):
#            continue
#        #print("calling crawler", sub_url)
#        crawl(sub_url, found, home_site, rp, D, depth-1)
#        #D.update(more_d)
#    #print(parser.text)
#    #return(D)
#    #print(parser.d)
