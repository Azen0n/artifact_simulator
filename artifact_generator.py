import json
import random
from copy import deepcopy
from dataclasses import dataclass, field
from datatypes import Artifact, ArtifactType, Domain, Set, MainStat, SubStat

DOMAINS = ['Domain of Guyun',
           'Midsummer Courtyard',
           'Valley of Remembrance',
           'Hidden Palace of Zhou Formula',
           'Peak of Vindagnyr',
           'Ridge Watch',
           'Momiji-Dyed Court',
           'Slumbering Court',
           'Clear Pool and Mountain Cavern']

ARTIFACT_TYPE_NAMES = [
    'Flower of Life',
    'Plume of Death',
    'Sands of Eon',
    'Goblet of Eonothem',
    'Circlet of Logos'
]

SUB_STATS_RANGES = [
    [0, 0],
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4]
]


@dataclass
class ArtifactGenerator:
    _rarities: list[list[ArtifactType]] = field(default_factory=list)
    _domains: list[Domain] = field(default_factory=list)

    def __post_init__(self):
        for i in range(5):
            main_stats = get_artifact_main_stats(str(i + 1))
            sub_stats = get_artifact_sub_stats(str(i + 1))
            rarity_stats = [ArtifactType(ARTIFACT_TYPE_NAMES[j], main_stats[j], sub_stats) for j in range(5)]
            self._rarities.append(rarity_stats)
        self._domains = get_domains()

    def grand_roll(self, domain_name: str):
        domain = self.__find_domain(domain_name)
        artifact_rarities = [*[5] * random.choices([1, 2], [0.93, 0.07], k=1)[0],
                             *[4] * random.choices([2, 3], [0.52, 0.48], k=1)[0],
                             *[3] * random.choices([3, 4], [0.45, 0.55], k=1)[0]]
        artifacts = []
        for rarity in artifact_rarities:
            artifact = self.roll(domain, rarity)
            artifacts.append(artifact)
        return artifacts

    def roll(self, domain: Domain, rarity: int):
        artifact_set = random.choice(domain.get_suitable_sets(rarity))
        artifact_rarity = deepcopy(self._rarities[rarity - 1])
        artifact_type_index = random.randint(0, 4)
        artifact_type = artifact_rarity[artifact_type_index]

        artifact = Artifact(name=artifact_set.artifact_names[artifact_type_index],
                            type=artifact_type,
                            rarity=rarity,
                            main_stat=artifact_type.get_random_main_stat(),
                            sub_stats=artifact_type.get_random_sub_stats(random.choice(SUB_STATS_RANGES[rarity - 1])),
                            set=artifact_set)
        return artifact

    def __find_domain(self, domain_name: str) -> Domain:
        for domain in self._domains:
            if domain.name == domain_name:
                return domain
        raise ValueError(f'Domain \'{domain_name}\' not found.')


def get_domains() -> list[Domain]:
    with open('data/sets_from_domains.json', 'r') as file:
        sets = json.load(file)

    domains = []
    for i, domain in enumerate(DOMAINS):
        domains.append(Domain(domain))
        for j in sets.keys():
            if domain in sets[j]['obtain_locations'][sets[j]['rarities'][0]]:
                domain_set = Set(name=sets[j]['name'],
                                 artifact_names=sets[j]['artifact_names'],
                                 artifact_images=sets[j]['artifact_images'],
                                 bonuses=sets[j]['bonuses'],
                                 rarities=sets[j]['rarities'],
                                 obtain_locations=sets[j]['obtain_locations'])
                domains[i].sets.append(domain_set)
    return domains


def get_artifact_main_stats(rarity: str) -> list[list[MainStat]]:
    with open('data/main_stats.json', 'r') as file:
        stats = json.load(file)

    main_stats = []
    for i, artifact_type in enumerate(stats[rarity]):
        main_stats.append([])
        for stat in stats[rarity][artifact_type]:
            main_stat = MainStat(name=stat['name'],
                                 min=stat['min'],
                                 max=stat['max'],
                                 probability=stat['probability'])
            main_stats[i].append(main_stat)
    return main_stats


def get_artifact_sub_stats(rarity: str) -> list[SubStat]:
    with open('data/sub_stats.json', 'r') as file:
        stats = json.load(file)

    sub_stats = []
    for stat in stats[rarity]:
        sub_stat = SubStat(name=stat['name'],
                           possible_values=stat['possible_values'],
                           probability=stat['probability'])
        sub_stats.append(sub_stat)
    return sub_stats
