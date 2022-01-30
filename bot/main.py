from enum import Enum
import discord
from artifact_generator import ArtifactGenerator, DOMAINS
from datatypes import Artifact
from token_string import TOKEN

EMOJI = {
    'back': '⬅', 'reroll': '🔄', 'upgrade': '⬆',
    1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣', 9: '9️⃣'
}

ACTION = {
    '⬅': 'back', '🔄': 'reroll', '⬆': 'upgrade',
    '1️⃣': 1, '2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '5️⃣': 5, '6️⃣': 6, '7️⃣': 7, '8️⃣': 8, '9️⃣': 9
}


class Page(Enum):
    DOMAIN = 'Domain Selection'
    ARTIFACT_LIST = 'Artifact List'
    ARTIFACT = 'Artifact Info'


class Client(discord.Client):
    generator: ArtifactGenerator = None
    message: discord.Message = None
    current_domain: str = None
    current_artifact: Artifact = None
    current_page: Page = None
    current_user: discord.User = None

    def init_generator(self, generator: ArtifactGenerator):
        self.generator = generator

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if message.content.startswith('<@!936983390601773077>'):
            if self.message is not None:
                await self.__close_message(message.author)
            await self.__send_initial_message(message)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user == self.user:
            return
        if reaction.message != self.message:
            return
        if reaction.emoji in ACTION:
            if self.current_page == Page.DOMAIN:
                await self.__on_page_domain(reaction)
            elif self.current_page == Page.ARTIFACT_LIST:
                await self.__on_page_artifact_list(reaction)
            elif self.current_page == Page.ARTIFACT:
                await self.__on_page_artifact(reaction)

    async def on_message_delete(self, message: discord.Message):
        if message == self.message:
            self.message = None

    async def __send_initial_message(self, start_message: discord.Message):
        self.current_user = start_message.author
        embed = await self.__get_domain_embed()
        self.message = await start_message.channel.send(embed=embed)
        self.current_page = Page.DOMAIN
        for action in ACTION:
            await self.message.add_reaction(action)

    async def __close_message(self, user: discord.User):
        await self.message.edit(embed=self.message.embeds[0].set_footer(
            text=f'Closed by {user}',
            icon_url=user.avatar_url))

    async def __get_domain_embed(self) -> discord.Embed:
        domain_list = ''.join(f'`{i + 1}.` {domain}\n' for i, domain in enumerate(DOMAINS))

        embed = discord.Embed(title='Domain Reliquary: Tier EX')
        embed.add_field(name='Choose Domain:', value=domain_list)
        embed.set_thumbnail(url='https://static.wikia.nocookie.net/gensin-impact/images/b/b1/Emblem_Domains.png')
        embed.set_footer(text=f'Started by {self.current_user}', icon_url=self.current_user.avatar_url)
        return embed

    async def __on_page_domain(self, reaction: discord.Reaction):
        action = ACTION[reaction.emoji]
        if type(action) == int:
            self.current_domain = DOMAINS[action - 1]
            self.generator.grand_roll(self.current_domain)
            embed = await self.__get_artifact_list_embed()
            await self.message.edit(embed=embed)
            self.current_page = Page.ARTIFACT_LIST

    async def __on_page_artifact_list(self, reaction: discord.Reaction):
        action = ACTION[reaction.emoji]
        if type(action) == int:
            if action in range(1, len(self.generator.artifacts) + 1):
                self.current_artifact = self.generator.artifacts[action - 1]
                embed = await self.__get_artifact_embed()
                await self.message.edit(embed=embed)
                self.current_page = Page.ARTIFACT
        elif action == 'reroll':
            self.generator.grand_roll(self.current_domain)
            embed = await self.__get_artifact_list_embed()
            await self.message.edit(embed=embed)
        elif action == 'back':
            embed = await self.__get_domain_embed()
            await self.message.edit(embed=embed)
            self.current_page = Page.DOMAIN

    async def __on_page_artifact(self, reaction: discord.Reaction):
        action = ACTION[reaction.emoji]
        if action == 'upgrade':
            for _ in range(4):
                self.current_artifact.upgrade()
            embed = await self.__get_artifact_embed()
            await self.message.edit(embed=embed)
        elif action == 'back':
            embed = await self.__get_artifact_list_embed()
            await self.message.edit(embed=embed)
            self.current_page = Page.ARTIFACT_LIST

    async def __get_artifact_list_embed(self) -> discord.Embed:
        artifact_list = ''.join(f'`{i + 1}.` {artifact.to_string_short()}\n'
                                for i, artifact in enumerate(self.generator.artifacts))

        embed = discord.Embed(title='Domain Reliquary: Tier EX')
        embed.add_field(name=f'Got {len(self.generator.artifacts)} artifacts ({self.current_domain}):',
                        value=artifact_list,
                        inline=False)
        embed.add_field(name='Actions',
                        value=f'1️⃣-{EMOJI[len(self.generator.artifacts)]} Show Stats\n'
                              f'🔄 Roll New\n'
                              f'⬅ Choose Another Domain')
        embed.set_thumbnail(url=self.generator.artifacts[0].image_url)
        embed.set_footer(text=f'Started by {self.current_user}', icon_url=self.current_user.avatar_url)
        return embed

    async def __get_artifact_embed(self) -> discord.Embed:
        artifact_name, artifact_info = self.__artifact_to_string_for_embed()
        set_info = ''.join(f'\n⊘ {piece}: {self.current_artifact.set.bonuses[piece]}'
                           for piece in self.current_artifact.set.bonuses)

        embed = discord.Embed(title='Domain Reliquary: Tier EX')
        embed.add_field(name=artifact_name,
                        value=artifact_info,
                        inline=False)
        embed.add_field(name=f'{self.current_artifact.set.name}',
                        value=set_info,
                        inline=False)
        embed.add_field(name='Actions',
                        value=f'⬆ Upgrade\n'
                              f'⬅ Back')
        embed.set_thumbnail(url=self.current_artifact.image_url)
        embed.set_footer(text=f'Started by {self.current_user}', icon_url=self.current_user.avatar_url)
        return embed

    def __artifact_to_string_for_embed(self):
        artifact_name = f'{self.current_artifact.name} ({self.current_artifact.type.name})'
        sub_stats = ''.join(f"{stat.to_string()}\n" for stat in self.current_artifact.sub_stats)
        artifact_info = ''.join(
            f'{self.current_artifact.main_stat.to_string()}\n'
            f'{"★" * self.current_artifact.rarity}\n'
            f'────────────────────────────────\n'
            f'[+{self.current_artifact.level}]\n'
            f'{sub_stats}'
        )
        return artifact_name, artifact_info


def main():
    client = Client()
    client.init_generator(ArtifactGenerator())
    client.run(TOKEN)


if __name__ == '__main__':
    main()
