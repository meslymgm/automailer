from models import RSSSource

RSS_FEEDS = [
    RSSSource(name="PIB", url="https://www.pib.gov.in/ViewRss.aspx?reg=1&lang=1"),
    RSSSource(name="Hindu", url="https://www.thehindu.com/news/national/feeder/default.rss"),
    RSSSource(name="BBC", url="https://feeds.bbci.co.uk/news/rss.xml"),
]
