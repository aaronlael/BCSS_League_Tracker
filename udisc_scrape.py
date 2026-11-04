from urllib.parse import urlsplit

from bs4 import BeautifulSoup
import requests


class InvalidUDiscEventURL(ValueError):
    pass


def validate_udisc_event_url(url: str | None) -> str:
    if not isinstance(url, str):
        raise InvalidUDiscEventURL('Enter a valid UDisc event URL.')

    try:
        parsed = urlsplit(url.strip())
        port = parsed.port
    except ValueError as exc:
        raise InvalidUDiscEventURL('Enter a valid UDisc event URL.') from exc

    path_parts = parsed.path.strip('/').split('/')
    if (
        parsed.scheme != 'https'
        or parsed.hostname != 'udisc.com'
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
        or len(path_parts) != 2
        or path_parts[0] != 'events'
        or not path_parts[1]
        or not path_parts[1].isalnum()
        or parsed.fragment
    ):
        raise InvalidUDiscEventURL('Enter a valid UDisc event URL.')

    return f'https://udisc.com/events/{path_parts[1]}'


def scrape_results_page(url_code: str) -> list:
    event_url = validate_udisc_event_url(url_code)
    r = requests.get(
        event_url,
        timeout=(5, 20),
        allow_redirects=False,
    )
    if 300 <= r.status_code < 400:
        raise requests.exceptions.HTTPError(
            'UDisc event URL redirected; redirects are not followed.',
            response=r,
        )
    r.raise_for_status()
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('div', class_="w-full min-w-0 overflow-x-auto overflow-y-hidden rounded-lg")
    table = s.find('table')

    data = []
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            row_data.append(cell.text.strip())
        data.append(row_data)
    player_out = []
    for player in data:
        if len(player) > 0:
            if player[3] != "":
                player_out.append((player[0], player[1], player[-1]))
            else:
                player_out.append(("666", player[1], "666"))
    return player_out