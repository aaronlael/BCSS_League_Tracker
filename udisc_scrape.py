from bs4 import BeautifulSoup
import requests

def scrape_results_page(url_code: str) -> list:
    event_url = url_code


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
                player_out.append((player[0], player[1], player[-1]))
            else:
                player_out.append(("666", player[1], "666"))
    return player_out