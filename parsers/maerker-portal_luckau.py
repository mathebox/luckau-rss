from bs4 import BeautifulSoup
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from pathlib import Path
import requests

def parse():
    base_url = 'https://maerker.brandenburg.de/bb/luckau'

    fg = FeedGenerator()
    fg.id(base_url)
    fg.title('Maerker Portal - Luckau')
    fg.link(href=base_url, rel='self')
    fg.language('de')
    fg.description('Meldungen auf dem Maerker Portal für die Stadt Luckau')

    try:
        for skip_items in range(0, 30, 5):
            url = base_url + f"?skip={skip_items}"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')

            for article in soup.find_all('article'):
                container = article.find('div', class_='hinweis')

                content_container = container.find('div', class_='eightcol')
                entry_title = content_container.find('h3').string.strip()
                
                id_container = content_container.find('p', class_='small')
                for strong in id_container.find_all('strong'):
                    if strong.string == 'ID:':
                        entry_id = strong.next_sibling.string.strip()
                entry_url = f"https://maerker.brandenburg.de/bb/luckau?_id={entry_id}"

                description = id_container.next_sibling.getText().strip()

                metacontent_container = container.find('div', class_='last')
                pub_date_str = metacontent_container.find('strong').string.strip()
                pub_date = datetime.strptime(pub_date_str, '%d.%m.%Y, %H:%M Uhr').replace(tzinfo=timezone.utc)

                location = metacontent_container.find('p').contents[0].getText().strip()

                if location == 'Luckau':
                    fe = fg.add_entry()
                    fe.id(entry_url)
                    fe.title(entry_title)
                    fe.link(href=entry_url)
                    fe.pubDate(pub_date)
                    fe.description(description)
    except Exception as e:
        print('Error while creating rss feed:', e)

    if len(fg.entry()) < 1:
        fe = fg.add_entry()
        fe.id(f"error-{datetime.now().isoformat()}")
        fe.title('Error parsing website')
        fe.link(href=url)    

    current_file_path = Path(__file__).parent.resolve()
    rss_path = current_file_path.parent / 'generated-rss'
    rss_path.mkdir(parents=True, exist_ok=True)
    fg.rss_file(rss_path / 'maerker-protal_luckau.xml')


if __name__ == "__main__":
    parse()
