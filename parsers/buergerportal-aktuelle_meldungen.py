from bs4 import BeautifulSoup
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from pathlib import Path
import requests

def parse():
    url = 'https://luckau.de/de/buergerportal/aktuelles/aktuelle-meldungen.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    fg = FeedGenerator()
    fg.id(url)
    fg.title('Bürgerportal - Aktuelle Meldungen')
    fg.link(href=url, rel='self')
    fg.language('de')
    fg.description('Aktuelle Meldungen')

    try:
        container = soup.find(id='article_aktuelle-meldungen')
        for article in container.find_all('article'):
            pub_date = article.find('p').string
            h2 = article.find('h2')
            h2_a = h2.find('a')
            headline = h2_a or h2
            entry_title = headline.string.strip()
            entry_url = article.find('a').get('href')
            entry_url = entry_url if entry_url.startswith('https://luckau.de') else 'https://luckau.de' + entry_url

            fe = fg.add_entry()
            fe.id(entry_url)
            fe.title(entry_title)
            fe.link(href=entry_url)
            fe.pubDate(datetime.strptime(pub_date, '%d.%m.%Y').replace(tzinfo=timezone.utc))

            paragraphs = article.find_all('p')
            if len(paragraphs) > 1:
                fe.description(paragraphs[1].string)
    except:
        print("Error while creating rss feed")

    if len(fg.entry()) < 1:
        fe = fg.add_entry()
        fe.id(f"error-{datetime.now().isoformat()}")
        fe.title('Error parsing website')
        fe.link(href=url)    

    current_file_path = Path(__file__).parent.resolve()
    rss_path = current_file_path.parent / 'generated-rss'
    rss_path.mkdir(parents=True, exist_ok=True)
    fg.rss_file(rss_path / 'buergerportal-akutelle_meldungen.xml')


if __name__ == "__main__":
    parse()
