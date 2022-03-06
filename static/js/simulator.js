$(document).ready(function () {
    const button = document.getElementById('roll');
    button.addEventListener('click', () => {
        const domainList = document.getElementById('selectDomain');
        const chosenDomain = domainList.options[domainList.selectedIndex].text;

        axios.get('roll/', {
            params: {
                domain: chosenDomain
            }
        })
            .then(function (response) {
                console.log(response);
                const artifactGrid = document.getElementById('artifactGrid');
                artifactGrid.innerHTML = '';
                for (const artifact of response.data['artifacts']) {
                    artifactGrid.appendChild(getHTMLArtifactCard(artifact));
                }
            });
    })
});

function getHTMLArtifactCard(artifact) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'artifact-card-container m-2';

    const artifactCard = document.createElement('div');
    artifactCard.className = 'artifact-card';
    artifactCard.innerHTML = '<img class="img-fluid" src="../static/img/artifact-card.svg" alt="">';

    const artifactCardImage = document.createElement('div');
    artifactCardImage.className = 'artifact-card-image';
    artifactCardImage.innerHTML = '<img class="img-fluid" src="' + artifact['image'] + '" alt="">';

    const artifactCardRarity = document.createElement('div');
    artifactCardRarity.className = 'artifact-card-rarity';
    artifactCardRarity.innerHTML = '<img class="img-fluid" src="/static/' + artifact['rarity_image_url'] + '" alt="">';

    const artifactCardLevel = document.createElement('div');
    artifactCardLevel.className = 'artifact-card-level';
    artifactCardLevel.innerHTML = '1';

    cardDiv.appendChild(artifactCard);
    cardDiv.appendChild(artifactCardImage);
    cardDiv.appendChild(artifactCardRarity);
    cardDiv.appendChild(artifactCardLevel);

    return cardDiv;
}