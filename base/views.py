from django.http import JsonResponse
from django.shortcuts import render
import math
import random

from artifact_generator import ArtifactGenerator, DOMAINS


class Artifact:
    image: str
    rarity: int
    level: int

    def __init__(self, image, rarity, level):
        self.image = image
        self.rarity = rarity
        self.level = level

    @property
    def rarity_image_url(self):
        return f'img/{self.rarity}_star_icon.png'


def split_in_rows_of_n_columns(list_: list, n: int) -> list[list]:
    new_list = []
    number_of_rows = math.floor(len(list_) / n)
    for i in range(number_of_rows + 1):
        new_list.append([])
        for _ in range(n):
            try:
                new_list[i].append(list_.pop(0))
            except IndexError:
                break
    return new_list


def index(request):
    context = {
        'domains': DOMAINS,
    }
    return render(request, 'index.html', context)


def storage(request):
    artifacts = [Artifact('https://static.wikia.nocookie.net/gensin-impact/images/0/0f/Item_Witch%27s_Flower_of_Blaze.png', 4, random.randint(0, 20)) for _ in range(50)]

    context = {
        'artifacts': artifacts,
    }
    return render(request, 'storage.html', context)


def roll(request):
    generator = ArtifactGenerator()
    domain = request.GET.get('domain')
    result = generator.grand_roll(domain)

    artifacts = []
    for artifact in result:
        artifacts.append({'name': artifact.name, 'image': artifact.image_url, 'rarity_image_url': f'img/{artifact.rarity}_star_icon.png'})

    context = {
        'artifacts': artifacts,
    }
    return JsonResponse(context)
