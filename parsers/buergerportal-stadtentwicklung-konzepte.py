from bs4 import BeautifulSoup
from datetime import datetime
from feedgen.feed import FeedGenerator
from pathlib import Path
import requests

def parse():
    url = 'https://luckau.de/de/buergerportal/stadtentwicklung/konzepte.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    fg = FeedGenerator()
    fg.id(url)
    fg.title('Bürgerportal - Stadtentwicklung - Konzepte')
    fg.link(href=url, rel='self')
    fg.language('de')
    fg.description('Konzepte der Stadtentwicklung')

    try:
        for item in soup.find_all('h3'):
            if link := item.find('a'):
                entry_title = link.string
                fe = fg.add_entry()
                fe.id(entry_title)
                fe.title(entry_title)
                fe.link(href=url)

                print("Added entry \n" \
                      f"> URL: {url} \n" \
                      f"> title: {entry_title} \n" \
                      )

    except Exception as e:
        print('Error while creating rss feed')
        print('> ', e)

    if len(fg.entry()) < 1:
        fe = fg.add_entry()
        fe.id(f"error-{datetime.now().isoformat()}")
        fe.title('Error parsing website')
        fe.link(href=url)

    current_file_path = Path(__file__).parent.resolve()
    rss_path = current_file_path.parent / 'generated-rss'
    rss_path.mkdir(parents=True, exist_ok=True)
    fg.rss_file(rss_path / 'buergerportal-stadtentwicklung-konzepte.xml')


if __name__ == "__main__":
    parse()
