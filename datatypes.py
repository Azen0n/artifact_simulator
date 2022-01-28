from dataclasses import dataclass, field
from enum import Enum
import random
from artifact_info import *


@dataclass
class Set:
    name: str
    rarity: list[int]
    bonus: dict[int, str]
    domains: list[str]


@dataclass
class MainStat:
    name: str
    min: float
    max: float
    probability: float = None
    level: int = 0

    @property
    def value(self) -> float:
        return round(self.values[self.level], 1)

    @property
    def values(self) -> list[float]:
        return [self.min + (self.max - self.min) / 20 * i for i in range(21)]

    def upgrade(self):
        self.level += 1

    def print(self):
        if '%' in self.name:
            print(self.name[:-4])
            print(self.value)
        else:
            print(self.name)
            print(round(self.value))


@dataclass
class SubStat:
    name: str
    max: float
    probability: float = None
    proc_history: list[float] = field(default_factory=list)

    def __post_init__(self):
        self.upgrade()

    @property
    def value(self) -> float:
        return round(sum(self.proc_history), 1)

    @property
    def possible_values(self) -> list[float]:
        return [self.max - self.max * i / 10 for i in range(4)]

    def upgrade(self):
        self.proc_history.append(random.choice(self.possible_values))

    def print(self):
        if '%' in self.name:
            print(f'{self.name[:-4]}+{self.value}%')
        else:
            print(f'{self.name}+{round(self.value)}')


@dataclass
class ArtifactTypeInfo:
    name: str
    main_stats: list[MainStat]
    sub_stats: list[SubStat]

    @property
    def main_probabilities(self) -> list[float]:
        return [stat.probability for stat in self.main_stats]

    @property
    def sub_probabilities(self) -> list[float]:
        return [stat.probability for stat in self.sub_stats]

    def get_random_sub_stats(self, number_of_stats: int) -> list[SubStat]:
        random_sub_stats = []
        for _ in range(number_of_stats):
            stat = random.choices(self.sub_stats, weights=self.sub_probabilities, k=1)[0]
            random_sub_stats.append(stat)
            self.delete_sub_stat(stat.name)
        return random_sub_stats

    def delete_sub_stat(self, name: str):
        for stat in self.sub_stats:
            if stat.name == name:
                self.sub_stats.remove(stat)
        self.__recalculate_sub_probabilities()

    def __recalculate_sub_probabilities(self):
        if sum(self.sub_probabilities) != 1.0:
            for stat in self.sub_stats:
                stat.probability /= sum(self.sub_probabilities)

    def get_random_main_stat(self):
        return random.choices(self.main_stats, weights=self.main_probabilities, k=1)[0]


class ArtifactType(Enum):
    FLOWER = ArtifactTypeInfo('Flower of Life', [MainStat(*s) for s in flower_main], [SubStat(*s) for s in sub])
    PLUME = ArtifactTypeInfo('Plume of Death', [MainStat(*s) for s in plume_main], [SubStat(*s) for s in sub])
    SANDS = ArtifactTypeInfo('Sands of Eon', [MainStat(*s) for s in sands_main], [SubStat(*s) for s in sub])
    GOBLET = ArtifactTypeInfo('Goblet of Eonothem', [MainStat(*s) for s in goblet_main], [SubStat(*s) for s in sub])
    CIRCLET = ArtifactTypeInfo('Circlet of Logos', [MainStat(*s) for s in circlet_main], [SubStat(*s) for s in sub])


@dataclass
class Artifact:
    name: str
    type: ArtifactType
    rarity: int
    main_stat: MainStat
    sub_stats: list[SubStat]
    level: int = 0

    def __post_init__(self):
        self.type.value.delete_sub_stat(self.main_stat.name)

    def upgrade(self):
        if self.level < 20:
            self.level += 1
            self.main_stat.upgrade()
            if self.level % 4 == 0:
                self.__upgrade_sub_stats()
        else:
            print('Max Level Reached')

    def __upgrade_sub_stats(self):
        if len(self.sub_stats) < 4:
            self.sub_stats.append(self.type.value.get_random_sub_stats(1)[0])
        else:
            random.choice(self.sub_stats).upgrade()

    def print(self):
        print(f'\n{self.name} ({self.type.value.name})')

        self.main_stat.print()

        for _ in range(self.rarity):
            print('★', end='')
        print(f'     [+{self.level}]')
        print('--------------------------')
        for stat in self.sub_stats:
            stat.print()
