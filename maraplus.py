import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from collections import defaultdict


# получаем текст html-страницы
def get_html(url):
    r = requests.get(url)
    return r.text


# получаем все ивэнты для марафона на теннис
def get_all_event_marathonbet(html):
    all_players = []
    all_K = []
    soup = BeautifulSoup(html, 'lxml')
    all_event = soup.find('div', class_ = "sport-category-content").find_all('div', class_='bg coupon-row')
    for players in all_event:
        players = players['data-event-name'].replace('- ', '.').split('.')
        player_1 = players[1].strip()
        player_2 = players[3].strip()
        all_players.append(player_1)
        all_players.append(player_2)

    for g in all_event:
        K1 = g.find('td',colspan="1").find('span',class_="selection-link active-selection").text
        K2 = g.find('td', colspan="1").find('span', class_="selection-link active-selection").findNext('span').text
        all_K.append(K1)
        all_K.append(K2)

    return all_players, all_K


# получаем ссылки на все события
def get_all_href_plusminus(html):
    arr_href =[]
    soup = BeautifulSoup(html, 'lxml')
    all_lines = soup.find('div', class_='bcontent').find_all('td', class_='turspis')
    for all_event_href in all_lines:
        a_s = all_event_href.find_all('a')
        for href in a_s:
            arr_href.append(href['href'])
    return arr_href


# получаем все ивэнты на теннис для плюсминус
def get_all_event_plusminus(arr_href):
    main_url = 'http://plusminus.by/bet.php'
    all_players = []
    all_K = []
    for href in arr_href:
        url = main_url+href
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        tbodys = soup.find('table',class_ = 'line_table').find_all('tbody',onclick="ccolor(event,this);")
        for tbody in tbodys:
            couple = tbody.find('td',width="300").text.split(' ')
            if '(srl)' not in couple:
                K1 = tbody.find('td', width="300").findNext('td').text
                K2 = tbody.find('td', width="300").findNext('td').findNext('td').text

                all_players.append(couple[0])
                all_players.append(couple[couple.index('-') + 1])
                all_K.append(K1)
                all_K.append(K2)

    return all_players, all_K


def create_arr_couple(arr_players):
    arr_couple = []
    for i in range(0, len(arr_players), 2):
        arr_couple.append(arr_players[i] + ' V ' + arr_players[i + 1])
    return arr_couple


def create_dict(arr_couple, arr_key):
    cat = defaultdict(list)
    scet = 0
    try:
        for i in range(len(arr_couple)):
            cat[arr_couple[i]].append(arr_key[scet])
            cat[arr_couple[i]].append(arr_key[scet + 1])
            scet += 2
        return dict(cat)
    except IndexError:
        print('Количество игроков не совпадает с количеством кэфов')


# находим одинаковые события
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# находим вилку
def find_vilka(K1, K2):
    return 1/float(K1)+1/float(K2)

# считаем, сколько составит чистый выигрыш
def profit(K, summa_max,summa_min):
    print("Выигрыш составит: "+str((float(K)*summa_max)-summa_min-summa_max))


def raschet_vilki(K1,K2,summa_max = 100):

    if K1<K2:
        summa_min = (float(K1)*summa_max)/float(K2)
        print('На коэффициент {}'.format(K1)+' ставим {} '.format(summa_max))
        print('На коэффициент {}'.format(K2) + ' ставим {} '.format(summa_min))
        profit(K1, summa_max, summa_min)

    else:
        summa_min = (float(K2) * summa_max) / float(K1)
        print('На коэффициент {}'.format(K1) + ' ставим {} '.format(summa_min))
        print('На коэффициент {}'.format(K2) + ' ставим {} '.format(summa_max))
        profit(K2, summa_max, summa_min)


# находим общие матчи для двух контор
def find_general(a_couple, b_couple, dict_a, dict_b):
    for elem_a in a_couple:
        for elem_b in b_couple:
            d = similar(elem_a, elem_b)
            if d > 0.9:

                arr_K_a = dict_a[elem_a]
                arr_K_b = dict_b[elem_b]
                Ko_1 = find_vilka(arr_K_a[0], arr_K_b[1])
                Ko_2 = find_vilka(arr_K_a[1], arr_K_b[0])
                print(elem_a)
                print(elem_b)
                print("Ko_1: " + str(Ko_1))
                print("Ko_1: " + str(Ko_2))

                if Ko_1<1:
                    raschet_vilki(arr_K_a[0], arr_K_b[1])

                if Ko_2<1:
                    raschet_vilki(arr_K_a[1], arr_K_b[0])


def main():
    url_marathonbet = 'https://www.marathonbet.by/su/popular/Tennis+-+2398'
    html_marathonbet = get_html(url_marathonbet)
    all_players_marathonbet, all_K_marathonbet = get_all_event_marathonbet(html_marathonbet)
    arr_couple_marathonbet = create_arr_couple(all_players_marathonbet)
    marathonbet_dict = create_dict(arr_couple_marathonbet, all_K_marathonbet)

    url_plusminus = 'http://plusminus.by/bet.php?events=3'
    html_plusminus = get_html(url_plusminus)
    arr_href = get_all_href_plusminus(html_plusminus)
    all_players_plusminus, all_K_plusminus = get_all_event_plusminus(arr_href)
    arr_couple_plusminus = create_arr_couple(all_players_plusminus)
    plusminus_dict = create_dict(arr_couple_plusminus, all_K_plusminus)

    find_general(arr_couple_marathonbet, arr_couple_plusminus , marathonbet_dict, plusminus_dict)


#test
if __name__ == '__main__':
    main()
