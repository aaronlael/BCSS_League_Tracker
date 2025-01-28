from bs4 import BeautifulSoup
import requests

def scrape_results_page() -> list:

    # get event URL from league events page
    URL = "https://udisc.com/leagues/breaking-chains-sober-sundays-t0YwuH/schedule"
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('a', class_="text-link group flex flex-col items-center gap-2 hover:no-underline md:flex-row border-divider hover:bg-bg-accent1 mt-1 rounded-lg border px-2 pb-3 pt-1")
    event_url = "https://udisc.com" + s['href'] + "/leaderboard?round=1"

    # testing
    event_url = "https://udisc.com" + "/events/breaking-chains-sober-sundays-breaking-chains-sober-sundays-Lz7cUA" + "/leaderboard?round=1"

    # get event results
    r = requests.get(event_url)
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
                player_out.append((player[0], player[1]))
            else:
                player_out.append(("666", player[1]))
    return player_out