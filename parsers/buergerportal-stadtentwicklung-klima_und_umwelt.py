from bs4 import BeautifulSoup
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import locale
from pathlib import Path
import requests

def parse():
    url = 'https://luckau.de/de/buergerportal/stadtentwicklung/klima-und-umwelt.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    locale.setlocale(locale.LC_TIME, "de_DE")

    fg = FeedGenerator()
    fg.id(url)
    fg.title('Bürgerportal - Stadtentwicklung - Klima und Umwelt')
    fg.link(href=url, rel='self')
    fg.language('de')
    fg.description('Meldungen aus der Stadtentwicklung zu Klima und Umwelt')

    try:
        # Aktuelles
        container = soup.find(id='article_6340')
        for headline in container.find_all('h2'):
            entry_title = headline.get_text()
            pub_date_str = headline.next_sibling.get_text()
            pub_date = datetime.strptime(pub_date_str, 'Veröffentlichungsdatum %d. %B %Y').replace(tzinfo=timezone.utc)
            description = headline.next_sibling.next_sibling.get_text()

            fe = fg.add_entry()
            fe.id(entry_title)
            fe.title(entry_title)
            fe.link(href=url)
            fe.pubDate(pub_date)
            fe.description(description)

        # Ältere Meldungen
        for older_container in container.find_all('div', class_='accordionWrapper'):
            entry_title = older_container.find('h3').get_text()
            description = older_container.find('div', class_='article').get_text()

            fe = fg.add_entry()
            fe.id(entry_title)
            fe.title(entry_title)
            fe.link(href=url)
            fe.description(description)
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
    fg.rss_file(rss_path / 'buergerportal-stadtentwicklung-klima_und_umwelt.xml')


if __name__ == "__main__":
    parse()
