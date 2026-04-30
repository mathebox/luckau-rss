from datetime import datetime
from feedgen.feed import FeedGenerator
from pathlib import Path
import requests

def parse():
    base_url = 'https://maerker.brandenburg.de/maerker/de/#/kommune/luckau/'
    js_url = 'https://maerker-buerger.brandenburg.de/maerker-brandenburg.js'
    local_authority_luckau = 3
    issues_url = f'https://maerker-redaktion.brandenburg.de/api/issues?localAuthority={local_authority_luckau}'

    fg = FeedGenerator()
    fg.id(base_url)
    fg.title('Maerker Portal - Luckau')
    fg.link(href=base_url, rel='self')
    fg.language('de')
    fg.description('Meldungen auf dem Maerker Portal für die Stadt Luckau')

    # Find Bearer token
    r = requests.get(js_url)
    part_2 = r.text.split('apiToken: $B("')[1]
    bearer_token = part_2.split('"')[0]
    auth_header_value = f'Bearer {bearer_token}'

    try:
        for page in range(1, 11):
            url = issues_url + f"&page={page}"
            r = requests.get(url, headers={
                "Authorization": auth_header_value
            })
            for item in r.json().get('data'):
                district = item.get('district', '')
                entry_title = item.get('title', 'unknown')
                entry_url = f"https://maerker.brandenburg.de/maerker/de/#/meldung/{item['id']}"
                pub_date = item.get('createdAt')
                description = item.get('description', '')

                if district in ['Luckau', '']:
                    fe = fg.add_entry()
                    fe.id(entry_url)
                    fe.title(entry_title)
                    fe.link(href=entry_url)
                    fe.pubDate(pub_date)
                    fe.description(description)
                    print("Added entry \n" \
                          f"> URL: {entry_url} \n" \
                          f"> title: {entry_title} \n" \
                          f"> date: {pub_date} \n" \
                          f"> {description} \n"
                          )
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
    fg.rss_file(rss_path / 'maerker-portal_luckau.xml')


if __name__ == "__main__":
    parse()
