from artifact_generator import ArtifactGenerator


if __name__ == '__main__':
    generator = ArtifactGenerator()
    artifact = generator.roll()
    artifact.print()

    while True:
        answer = input('\n(1) Upgrade (2) Roll New\n')

        if answer == '1':
            artifact.upgrade()
        else:
            artifact = generator.roll()

        artifact.print()
