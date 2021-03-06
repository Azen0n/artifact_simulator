from dataclasses import dataclass, field
import random


@dataclass
class Set:
    name: str
    artifact_names: list[str]
    artifact_images: list[str]
    bonuses: dict[str, str]
    rarities: list[int]
    obtain_locations: dict[int, list[str]]

    def print_info(self):
        print(f'{self.name}:')
        for piece in self.bonuses:
            print(f'⊘ {piece}: {self.bonuses[piece]}')


@dataclass
class Domain:
    name: str
    sets: list[Set] = field(default_factory=list)

    def get_suitable_sets(self, rarity: int) -> list[Set]:
        suitable_sets = []
        for artifact_set in self.sets:
            if str(rarity) in artifact_set.rarities:
                suitable_sets.append(artifact_set)
        if not suitable_sets:
            raise ValueError('Chosen Domain doesn\'t have sets of this rarity.')
        return suitable_sets


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
            print(f'{round(self.value, 1)}%')
        else:
            print(self.name)
            print(round(self.value))


@dataclass
class SubStat:
    name: str
    possible_values: list[float]
    probability: float = None
    proc_history: list[float] = field(default_factory=list)

    def __post_init__(self):
        self.upgrade()

    @property
    def value(self) -> float:
        return sum(self.proc_history)

    def upgrade(self):
        self.proc_history.append(random.choice(self.possible_values))

    def print(self):
        if '%' in self.name:
            print(f'{self.name[:-4]}+{round(self.value, 1)}%')
        else:
            print(f'{self.name}+{round(self.value)}')


@dataclass
class ArtifactType:
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


@dataclass
class Artifact:
    name: str
    type: ArtifactType
    rarity: int
    main_stat: MainStat
    sub_stats: list[SubStat]
    set: Set
    level: int = 0

    def __post_init__(self):
        self.type.delete_sub_stat(self.main_stat.name)

    def upgrade(self):
        if self.level < self.rarity * 4:
            self.level += 1
            self.main_stat.upgrade()
            if self.level % 4 == 0:
                self.__upgrade_sub_stats()
        else:
            print('Max Level Reached')

    def __upgrade_sub_stats(self):
        if len(self.sub_stats) < 4:
            self.sub_stats.append(self.type.get_random_sub_stats(1)[0])
        else:
            random.choice(self.sub_stats).upgrade()

    def print(self):
        print(f'\n{self.name} ({self.type.name})')

        self.main_stat.print()

        for _ in range(self.rarity):
            print('★', end='')
        print(f'     [+{self.level}]')
        print('--------------------------')
        for stat in self.sub_stats:
            stat.print()

    def print_short(self):
        print(f'{self.rarity}★ {self.name}')
