from artifact_generator import ArtifactGenerator, DOMAINS
from datatypes import Artifact


def choose_domain() -> str:
    print('Choose Domain:')
    for i, domain in enumerate(DOMAINS):
        print(f'{i + 1}. {domain}')

    domain_index = get_validated_answer()

    while int(domain_index) < 1 or int(domain_index) > len(DOMAINS):
        print('Wrong number.')
        domain_index = input()

    return DOMAINS[int(domain_index) - 1]


def get_validated_answer(commands: str = ''):
    """Input must be int."""
    answer = input(commands)
    while not answer.isdigit():
        print('Wrong number.')
        answer = input()
    return int(answer)


def print_artifact_list(artifacts: list[Artifact]):
    for i, artifact in enumerate(artifacts):
        print(f'{i + 1}. {artifact.to_string_short()}')


def main():
    generator = ArtifactGenerator()
    domain_name = choose_domain()
    artifacts = generator.grand_roll(domain_name)
    print_artifact_list(artifacts)

    artifact_info_commands = f'\n(1) Upgrade (2) Set Info (3) Back\n'
    while True:
        list_commands = f'\n(1-{len(artifacts)}) Show Stats (0) Roll New ({len(artifacts) + 1}) Choose Another Domain\n'
        answer = get_validated_answer(list_commands)

        if answer in range(1, len(artifacts) + 1):
            artifact_index = answer - 1
            print(artifacts[artifact_index])

            answer = get_validated_answer(artifact_info_commands)

            while answer == 2:
                print(artifacts[artifact_index].set.bonuses_to_string())
                answer = get_validated_answer(artifact_info_commands)

            while answer == 1:
                artifacts[artifact_index].upgrade()
                print(artifacts[artifact_index])
                answer = get_validated_answer(artifact_info_commands)

                while answer == 2:
                    print(artifacts[artifact_index].set.bonuses_to_string())
                    answer = get_validated_answer(artifact_info_commands)

            print()
            print_artifact_list(artifacts)

        elif answer == 0:
            artifacts = generator.grand_roll(domain_name)
            print_artifact_list(artifacts)

        elif answer == len(artifacts) + 1:
            domain_name = choose_domain()
            artifacts = generator.grand_roll(domain_name)
            print_artifact_list(artifacts)

        else:
            print('Wrong command.')


if __name__ == '__main__':
    main()
