let cardCollection = [];

async function fetchCards() {
    const response = await fetch('http://127.0.0.1:8082/cards', {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    });

    const jsonData = await response.json();

    return jsonData;
}

function renderCards(cards) {
    const cardContainer = document.querySelector("#card-container");

    for (card of cards) {
        const { label, description, category } = card;
        const cardDomElement = document.createElement("div");

        const labelDomElement = document.createElement("h3");
        labelDomElement.textContent = label;

        const descriptionDomElement = document.createElement("p");
        descriptionDomElement.textContent = description;

        cardDomElement.appendChild(labelDomElement);
        cardDomElement.appendChild(descriptionDomElement);
        cardDomElement.appendChild(document.createElement("hr"));

        cardContainer.appendChild(cardDomElement);
    }
}

function renderCard(card) {
    const { label, description, category } = card;

    const cardContainer = document.querySelector("#card-container");
    cardContainer.textContent = label;
}

document.addEventListener("DOMContentLoaded", async function () {
   const currentIndex = 2;

   const previousButton = document.querySelector("#previous-card");
   previousButton.addEventListener("click", function () {
    console.log("Previous button has been clicked!");
   });

   const flipButton = document.querySelector("#flip-card");
   let flipped = false;
   flipButton.addEventListener("click", function () {
    const cardContainer = document.querySelector("#card-container");
    const currentCard = cardCollection[currentIndex];
    if (!flipped) {
        cardContainer.textContent = currentCard.description;
    } else {
        cardContainer.textContent = currentCard.label;
    }
    flipped = !flipped;
   });

   const nextButton = document.querySelector("#next-card");
   nextButton.addEventListener("click", function () {
    console.log("Next button has been clicked!");
   });


   cardCollection = await fetchCards();
   console.log(cardCollection[currentIndex]);
   renderCard(cardCollection[currentIndex]);


});
