import json
import requests
from copy import deepcopy
from bs4 import BeautifulSoup
from datatypes import MainStat, SubStat


ARTIFACT_TYPE_FOR_STATS = {
        'Flower of Life': [],
        'Plume of Death': [],
        'Sands of Eon': [],
        'Goblet of Eonothem': [],
        'Circlet of Logos': []
    }

FLOWER_PROB = [1.0]
PLUME_PROB = [1.0]
SANDS_PROB = [0.2668, 0.2668, 0.2668, 0.1, 0.1]
GOBLET_PROB = [0.2125, 0.2125, 0.2, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.025]
CIRCLET_PROB = [0.22, 0.22, 0.22, 0.1, 0.1, 0.1, 0.04]
SUB_STATS_PROB = [0.1364, 0.1364, 0.1364, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.06815, 0.06815]


def parse_stats(link: str) -> tuple[dict, dict]:
    stats_page = requests.get(link)
    soup = BeautifulSoup(stats_page.text, 'html.parser')
    stats_tables = soup.find_all('table', {'class': 'wikitable'})
    main_stats = parse_main_stats(stats_tables[:5])
    sub_stats = parse_sub_stats(stats_tables[-1])

    low_rarity_main_stats = parse_low_rarity_main_stats(main_stats)
    main_stats.update(low_rarity_main_stats)

    return main_stats, sub_stats


def parse_main_stats(tables) -> dict:
    main_stats = {
        3: deepcopy(ARTIFACT_TYPE_FOR_STATS),
        4: deepcopy(ARTIFACT_TYPE_FOR_STATS),
        5: deepcopy(ARTIFACT_TYPE_FOR_STATS)
    }
    for table in tables:
        table_rows = table.find_all('tr')
        artifact_type = table_rows[0].text.strip(' \n ')
        for row in table_rows[2:]:
            name = row.find('th').text
            if 'Energy' in name:
                name = 'Energy Recharge (%)'
            for i, rarity in enumerate(row.find_all('td')):
                stat_min, stat_max = rarity.text.replace(',', '').split(' - ')
                stat = MainStat(name, float(stat_min), float(stat_max))
                main_stats[i + 3][artifact_type].append(stat)
    return main_stats


def parse_sub_stats(table) -> dict[int, list[SubStat]]:
    stats = {i + 1: [] for i in range(5)}
    table_rows = table.find_all('tr')
    for row in table_rows[1:]:
        name = row.find('th').text
        for i, rarity in enumerate(row.find_all('td')):
            possible_values = [float(i) for i in rarity.text.split(' / ')]
            stats[i + 1].append(SubStat(name, possible_values))
    return stats


def parse_low_rarity_main_stats(high_rarity_main_stats):
    link = 'https://genshin-impact.fandom.com/wiki/Artifacts/Scaling'
    stats_page = requests.get(link)
    soup = BeautifulSoup(stats_page.text, 'html.parser')

    main_stats = {
        1: deepcopy(ARTIFACT_TYPE_FOR_STATS),
        2: deepcopy(ARTIFACT_TYPE_FOR_STATS)
    }
    for i, table in enumerate(soup.find_all('table', {'class': 'wikitable'})[3:5]):
        stats = parse_stats_scaling_table(table)
        for artifact_type in high_rarity_main_stats[3].keys():
            for stat in high_rarity_main_stats[3][artifact_type]:
                for s in stats:
                    if s.name == stat.name:
                        main_stats[2 - i][artifact_type].append(s)
                        break
    return main_stats


def parse_stats_scaling_table(table) -> list[MainStat]:
    stats = []
    table_rows = table.find_all('tr')
    for row in table_rows[1:]:
        name = row.find('th').text.strip(' \n')
        if '%' in name:
            if 'l DMG' in name:
                name = f'{name[:-1]} Bonus (%)'
            else:
                name = f'{name[:-1]} (%)'
        stat_min = row.find_all('td')[0].text.strip(' ')
        stat_max = row.find_all('td')[-1].text.strip(' ')
        stats.append(MainStat(name, float(stat_min), float(stat_max)))
    return stats


def append_main_stats_probabilities(stats):
    probabilities = [FLOWER_PROB, PLUME_PROB, SANDS_PROB, GOBLET_PROB, CIRCLET_PROB]
    for rarity in stats.keys():
        for i, artifact_type in enumerate(stats[rarity].keys()):
            for j, stat in enumerate(stats[rarity][artifact_type]):
                stat.probability = probabilities[i][j]


def append_sub_stats_probabilities(stats):
    for rarity in stats.keys():
        for j, stat in enumerate(stats[rarity]):
            stat.probability = SUB_STATS_PROB[j]


def save_main_stats_to_json(main_stats, file_name: str):
    serializable_stats = {}
    for rarity in main_stats.keys():
        serializable_stats[rarity] = {}
        for artifact_type in main_stats[rarity].keys():
            serializable_stats[rarity][artifact_type] = []
            for stat in main_stats[rarity][artifact_type]:
                serializable_stats[rarity][artifact_type].append(vars(stat))
    with open(f'../data/{file_name}.json', 'w', encoding='UTF-8') as file:
        json.dump(serializable_stats, file)


def save_sub_stats_to_json(sub_stats, file_name: str):
    serializable_stats = {}
    for rarity in sub_stats.keys():
        serializable_stats[rarity] = []
        for stat in sub_stats[rarity]:
            serializable_stats[rarity].append(vars(stat))
    with open(f'../data/{file_name}.json', 'w', encoding='UTF-8') as file:
        json.dump(serializable_stats, file)


def main():
    stats_link = 'https://genshin-impact.fandom.com/wiki/Artifacts/Stats'
    main_stats, sub_stats = parse_stats(stats_link)
    append_main_stats_probabilities(main_stats)
    append_sub_stats_probabilities(sub_stats)

    save_main_stats_to_json(main_stats, 'main_stats')
    save_sub_stats_to_json(sub_stats, 'sub_stats')


if __name__ == '__main__':
    main()
