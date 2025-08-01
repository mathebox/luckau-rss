from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from pathlib import Path
import pytz
import requests

date_replace_mapping = {
        "Januar": "01",
        "Februar": "02",
        "März": "03",
        "April": "04",
        "Mai": "05",
        "Juni": "06",
        "Juli": "07",
        "August": "08",
        "September": "09",
        "Oktober": "10",
        "November": "11",
        "Dezember": "12",
    }


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def parse_page(cal, url):
    tzinfo = pytz.timezone("Europe/Berlin")

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Stop if no more events are found
    if not soup.find('article'):
        return False

    for article in soup.find_all('article'):
        headline = article.select('.eventInfo .headline')[0]
        title = headline.getText().strip()
        description = article.select('.eventInfo')[0].contents[1].getText().strip()
        location = article.select('.eventData .location')[0].getText().strip()
        if article_link := headline.select('a'):
            link = f"https://luckau.de{article_link[0]['href']}"
        else:
            link = url

        datetime_elements = article.select('.eventData .dateTimeTxt')
        if len(datetime_elements) > 0:
            datetime_parts = article.select('.eventData .dateTimeTxt')[0].getText().strip().split()
        else:
            datetime_parts = ['08:00']

        has_end_time = len(datetime_parts) > 2
        if has_end_time:
            time_from_string = datetime_parts[0]
            time_to_string = datetime_parts[2]
        else:
            time_from_string = datetime_parts[0]

        date_from_string = replace_all(article.select('.eventData .date .dateFromTxt')[0].getText().strip(), date_replace_mapping)

        has_end_date = len(article.select('.eventData .date .dateToTxt')) > 0
        if has_end_date:
            date_to_string = replace_all(article.select('.eventData .date .dateToTxt')[0].getText().strip(), date_replace_mapping)

        try:
            match (has_end_date, has_end_time):
                case (True, _):
                    # use start and end date. all day event
                    date_from = datetime.strptime(date_from_string, '%d. %m %Y').replace(tzinfo=tzinfo).date()
                    date_to = datetime.strptime(date_to_string, '%d. %m %Y').replace(tzinfo=tzinfo).date()
                case (False, True):
                    # use start date as end date. use start and end time
                    date_from = datetime.strptime(f"{date_from_string} {time_from_string}", '%d. %m %Y %H:%M').replace(tzinfo=tzinfo)
                    date_to = datetime.strptime(f"{date_from_string} {time_to_string}", '%d. %m %Y %H:%M').replace(tzinfo=tzinfo)
                case (False, False):
                    # use start date as end date. use start time + 2h
                    date_from = datetime.strptime(f"{date_from_string} {time_from_string}", '%d. %m %Y %H:%M').replace(tzinfo=tzinfo)
                    date_to = datetime.strptime(f"{date_from_string} {time_from_string}", '%d. %m %Y %H:%M').replace(tzinfo=tzinfo) + timedelta(hours=2)
        except ValueError:
            continue

        event = Event()
        event.add('summary', title)
        event.add('dtstart', date_from)
        event.add('dtend', date_to)
        event.add('location', location)
        event.add('url', link)
        cal.add_component(event)

        print("Added event \n" \
              f"> title: {title} \n" \
              f"> date: {date_from} - {date_to} \n" \
              f"> location: {location} \n"
              f"> url: {link} \n" \
              f"> description: {description} \n" \
              )
        
    return True


def parse():
    beginning_of_year = datetime(datetime.today().year, 1, 1)

    cal = Calendar()
    cal.add('dtstart', beginning_of_year)
    cal.add('summary', 'Veranstaltungen in Luckau')

    base_url = 'https://luckau.de/de/kultur-stadtleben/veranstaltungskalender'
    site_part = '.html'
    date_filter = f"?dateFrom={beginning_of_year.strftime('%d.%m.%Y')}"

    url = base_url + site_part + date_filter
    still_parsing = parse_page(cal, url)
    pages_parsed = 1

    while still_parsing:
        site_part = f"/seite-{pages_parsed*20}.html"
        url = base_url + site_part + date_filter
        still_parsing = parse_page(cal, url)
        pages_parsed += 1

    current_file_path = Path(__file__).parent.resolve()
    ical_path = current_file_path.parent / 'generated-rss'
    ical_path.mkdir(parents=True, exist_ok=True)
    with open(ical_path / 'kultur_stadtleben-veranstaltungskalender.ics', 'wb') as f:
        f.write(cal.to_ical())


if __name__ == "__main__":
    parse()
