import requests
import time


import feedparser
from requests import get

base = ""
urls = ["https://feeds.feedburner.com/indianautosblog", "https://www.thetruthaboutcars.com/rss/feed/all", "https://www.thesupercarblog.com/feed/", "https://www.thecarexpert.co.uk/feed/", "https://www.thetorquereport.com/feed/", "https://bangshift.com/feed/", "https://feeds.feedburner.com/BestSellingCars-MattsBlog", "https://thekoreancarblog.com/feed/", "http://www.purosautos.com/feed/", "https://www.automotiveaddicts.com/feed", "https://www.oldcarsweekly.com/.rss/full/", "https://gaugemagazine.com/feed/", "https://mycarheaven.com/feed/", "https://machineswithsouls.com/feed/"]
# more writing
urls1 = ["https://www.dailycarblog.com/feed/", "https://www.topspeed.com/feed/", "https://news.barrett-jackson.com/feed", "https://silodrome.com/feed/", "https://autospies.com/rss.aspx", "https://trendingmotor.com/feed/", "https://autoscommunity.com/feed", "https://www.carcomplaints.com/news/feed.xml", "http://feeds.feedburner.com/Automoblognet", "https://disaffected-musings.com/feed/", "https://journal.classiccars.com/feed/"]
# more writing
urls2 = ["https://www.canhealth.com/feed/", "https://news.siamphone.com/feed/", "https://droidsans.com/feed/", "https://peopleofcolorintech.com/feed/", "http://www.ecns.cn/rss/rss.xml", "https://winbuzzer.com/feed/", "https://www.thurrott.com/windows/feed", "https://technext.ng/feed/", "https://techcabal.com/feed/", "https://feeds.feedburner.com/blogspot/tKRU", "https://www.techcityng.com/feed/", "https://www.benjamindada.com/rss/", "https://www.canhealth.com/feed/", "https://www.cbc.ca/cmlink/rss-technology", "https://blog.bestbuy.ca/feed"]

urls3 = ["https://chinadigitaltimes.net/feed/", "https://thediplomat.com/category/china-power/feed/", "https://china-environment-news.net/feed/", "http://www.nytimes.com/topic/destination/china/rss.xml", "http://feeds.beijingbulletin.com/rss/55582c89cb296d4c", "https://www.chinaentertainmentnews.com/feeds/posts/default", "https://news.microsoft.com/feed/", "http://feeds.windowscentral.com/wmexperts", "https://blogs.windows.com/feed/", "https://mspoweruser.com/feed/" ,"https://www.zdnet.com/blog/microsoft/rss.xml", "https://msftnewsnow.com/feed/", "https://techcommunity.microsoft.com/plugins/custom/microsoft/o365/custom-blog-rss?tid=-3510255867542948717&size=25"]

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


