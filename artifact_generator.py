import random
from dataclasses import dataclass, field
from datatypes import Artifact, ArtifactType


types = [
    ArtifactType.FLOWER,
    ArtifactType.PLUME,
    ArtifactType.SANDS,
    ArtifactType.GOBLET,
    ArtifactType.CIRCLET
]


@dataclass
class ArtifactGenerator:
    _types: list[ArtifactType] = field(default_factory=lambda: types)

    def roll(self):
        artifact_type = random.choice(self._types)
        artifact = Artifact(name='Name',
                            type=artifact_type,
                            rarity=5,
                            main_stat=artifact_type.value.get_random_main_stat(),
                            sub_stats=artifact_type.value.get_random_sub_stats(random.choice([3, 4])))
        return artifact

