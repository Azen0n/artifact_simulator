import json
import requests
from copy import deepcopy
from bs4 import BeautifulSoup
from datatypes import Set
from artifact_generator import DOMAINS


def get_sets_links(sets_list_link: str) -> list[str]:
    sets_page = requests.get(sets_list_link)
    soup = BeautifulSoup(sets_page.text, 'html.parser')
    set_divs = soup.find_all('div', {'class': 'card_with_caption'})

    links = []
    for div in set_divs:
        links.append(f'https://genshin-impact.fandom.com{div.next.next["href"]}')
    return links[1:]  # Skip Initiate Set


def parse_sets(sets_links) -> list[Set]:
    sets_info = []
    for link in sets_links:
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        info_table = soup.find('aside')
        artifacts = info_table.find_all('a', {'class': 'image'})

        name = info_table.find('h2').text
        artifact_names = [artifact.next['alt'] for artifact in artifacts]
        artifact_images = [artifact['href'] for artifact in artifacts]
        bonuses = parse_bonuses(info_table)
        obtain_locations = parse_obtain_locations(info_table)
        rarities = list(obtain_locations.keys())
        fix_inconsistency(link, obtain_locations)

        sets_info.append(Set(name, artifact_names, artifact_images, bonuses, rarities, obtain_locations))
    return sets_info


def parse_bonuses(info_table):
    bonus_section = info_table.find_all('section')[0].find_all('div')
    bonuses = {}
    for i in range(0, len(bonus_section), 2):
        bonuses_text = bonus_section[i].text.split('\n')
        bonuses[bonuses_text[1]] = bonuses_text[2]
    return bonuses


def parse_obtain_locations(info_table):
    obtain_section = info_table.find_all('section')[1].find_all('div', recursive=False)
    obtain_locations = {}
    rarities = [i for i in obtain_section[0].text if i.isdigit()]
    for i, obtain_locations_div in enumerate(obtain_section[1:]):
        locations = [i.text for i in obtain_locations_div.find_all('div', {'class': 'pi-data-value'})]
        obtain_locations[rarities[i]] = locations
    return obtain_locations


def fix_inconsistency(link, obtain_locations):
    """These two sets' domains differs from other."""
    if link == 'https://genshin-impact.fandom.com/wiki/Heart_of_Depth' \
            or link == 'https://genshin-impact.fandom.com/wiki/Blizzard_Strayer':
        for rarity in obtain_locations:
            for i, location in enumerate(obtain_locations[rarity]):
                if 'Peak of Vindagnyr' in location:
                    obtain_locations[rarity][i] = 'Peak of Vindagnyr'


def get_sets_from_domains(sets_info: list[Set]) -> list[Set]:
    sets_from_domains = []
    for set in sets_info:
        delete_non_domain_locations(set)
        if set.obtain_locations:
            sets_from_domains.append(set)
    return sets_from_domains


def delete_non_domain_locations(set: Set):
    rarities = list(set.obtain_locations.keys())
    for rarity in rarities:
        domain_locations = []
        for location in set.obtain_locations[rarity]:
            if location in DOMAINS:
                domain_locations.append(location)
        if domain_locations:
            set.obtain_locations[rarity] = domain_locations
        else:
            del set.obtain_locations[rarity]
            set.rarities.remove(rarity)


def save_sets_to_json(sets, file_name: str):
    sets_dict = {}
    for i, set in enumerate(sets):
        sets_dict[i] = vars(set)
    with open(f'../data/{file_name}.json', 'w', encoding='UTF-8') as file:
        json.dump(sets_dict, file)


def main():
    sets_list_link = 'https://genshin-impact.fandom.com/wiki/Artifacts'
    sets_links = get_sets_links(sets_list_link)
    sets = parse_sets(deepcopy(sets_links))
    sets_from_domains = get_sets_from_domains(deepcopy(sets))
    save_sets_to_json(sets, 'sets')
    save_sets_to_json(sets_from_domains, 'sets_from_domains')


if __name__ == '__main__':
    main()
