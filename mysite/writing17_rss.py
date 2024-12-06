import requests
import time


import feedparser
from requests import get

base = ""
urls = ["https://www.makeuseof.com/feed/", "https://www.iphoneincanada.ca/feed/", "https://techcouver.com/feed/", "https://itnerd.blog/feed/", "https://betakit.com/feed/", "https://www.youtube.com/feeds/videos.xml?channel_id=UCsTcErHg8oDvUnTzoqsYeNw&x=1", "https://techrseries.com/feed/", "https://hrtechfeed.com/feed/", "https://testlify.com/feed/", "http://www.techlearning.com/feeds/all", "https://virtualschooling.wordpress.com/feed/", "http://www.eschoolnews.com/feed/", "https://blog.mimio.com/rss.xml", "https://classtechtips.com/feed/", "https://www.magicedtech.com/feed/"]
# more writing
urls1 = ["https://adtechdaily.com/feed/", "https://www.adexchanger.com/feed", "https://www.adweek.com/category/ad-tech/feed/", "https://sea-technology.com/feed", "https://www.marinetechnologynews.com/rss/news", "https://www.ship-technology.com/feed/", "https://splash247.com/category/sector/tech/feed/", "https://hackaday.com/feed", "https://blog.arduino.cc/feed/", "https://newatlas.com/index.rss", "https://innovationtoronto.com/feed/", "https://www.imnovation-hub.com/feed/", "https://bradenkelley.com/feed/", "https://www.trendhunter.com/rss", "https://www.openaccessgovernment.org/category/open-access-news/research-innovation-news/feed/"]
# more writing
urls2 = ["https://feeds.feedburner.com/TheHackersNews?format=xml", "https://www.grahamcluley.com/feed/", "https://www.schneier.com/blog/atom.xml", "https://www.csoonline.com/feed/", "https://www.darkreading.com/rss/all.xml", "https://www.infosecurity-magazine.com/rss/news/", "https://cyble.com/feed/", "https://medium.com/feed/@2ndsightlab", "https://davinciforensics.co.za/cybersecurity/feed/", "https://cybersecurity.att.com/site/blog-all-rss", "https://www.mcafee.com/blogs/feed/", "http://feeds.trendmicro.com/TrendMicroResearch", "https://www.bleepingcomputer.com/feed"]

urls3 = ["http://www.techrepublic.com/rssfeeds/topic/security/?feedType=rssfeeds", "https://www.proofpoint.com/us/rss.xml", "https://heimdalsecurity.com/blog/feed/", "http://securityaffairs.co/wordpress/feed", "https://www.tripwire.com/state-of-security/feed/", "https://www.secpod.com/blog/feed/", "https://www.cyberdefensemagazine.com/feed/", "https://socprime.com/feed/", "https://www.lastwatchdog.com/feed/", "https://any.run/cybersecurity-blog/feed/", "https://www.helpnetsecurity.com/feed/", "https://www.cm-alliance.com/cybersecurity-blog/rss.xml"]

for rss_url in urls:
    xml = base + rss_url

    # Limit feed output to 5 items
    # To disable limit simply do not provide the argument or use None
    feed = feedparser.parse(xml)
    # Print out feed meta data
    
    count = 0
    # Iteratively print feed items
    for item in feed.entries:
        print(xml + "  " + str(count))
        count += 1
        print(item.title)
        print(item.summary)
        
        r = requests.post('https://www.predictionary.us/B/posts/',data={'title':item.title, "body":item.summary, "url2": item.link})
        
        print(r.status_code)
        print(r.text)



for rss_url in urls1:
    xml = base + rss_url

    # Limit feed output to 5 items
    # To disable limit simply do not provide the argument or use None
    feed = feedparser.parse(xml)
    # Print out feed meta data
    
    count = 0
    # Iteratively print feed items
    for item in feed.entries:
        print(xml + "  " + str(count))
        count += 1
        print(item.title)
        print(item.summary)
        
        r = requests.post('https://www.predictionary.us/B/posts/',data={'title':item.title, "body":item.summary, "url2": item.link})
        
        print(r.status_code)
        print(r.text)


for rss_url in urls2:
    xml = base + rss_url

    # Limit feed output to 5 items
    # To disable limit simply do not provide the argument or use None
    feed = feedparser.parse(xml)
    # Print out feed meta data
    
    count = 0
    # Iteratively print feed items
    for item in feed.entries:
        print(xml + "  " + str(count))
        count += 1
        print(item.title)
        print(item.summary)
        
        r = requests.post('https://www.predictionary.us/B/posts/',data={'title':item.title, "body":item.summary, "url2": item.link})
        
        print(r.status_code)
        print(r.text)



for rss_url in urls3:
    xml = base + rss_url

    # Limit feed output to 5 items
    # To disable limit simply do not provide the argument or use None
    feed = feedparser.parse(xml)
    # Print out feed meta data
    
    count = 0
    # Iteratively print feed items
    for item in feed.entries:
        print(xml + "  " + str(count))
        count += 1
        print(item.title)
        print(item.summary)
        
        r = requests.post('https://www.predictionary.us/B/posts/',data={'title':item.title, "body":item.summary, "url2": item.link})
        
        print(r.status_code)
        print(r.text)


