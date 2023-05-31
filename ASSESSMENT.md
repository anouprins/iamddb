# Assessment Anou Prins

## TMDB database info opslaan in eigen database

Ik heb er voor gekozen dat elke keer dat er naar de serie pagina of movie pagina wordt gegaan er allereerst gekeken wordt naar of de data van dat item al in de IAMDDB database staat. Zoja, wordt die info gelijk gebruikt om de pagina te laden. Zonee, wordt er verbinding gemaakt met de TMDB database, en wordt de benodigde info daarvan bewaard in de IAMDDB database. Ik heb hiervoor gekozen om de aantal requests naar de TMDB database te verminderen. Aangezien deze info niet echt snel veranderd, was dit wel mogelijk voor deze pagina's. Niet voor bijvoorbeeld het berekenen van de gemiddelde popularity scorevoor de taste pagina. 

## het apart bewaren van database modellen en classes die database bewerken

Ik heb ervoor gekozen om alle database modellen in een map te houden, en vervolgens per database model een class te maken die die tables bewerkt. Zo is de code gescheiden. Ik had het achteraf iets algemener gemaakt. Dus algemene helpers functies maken die toepasbaar zouden zijn op die verschillende klasses. Maar het idee van gescheiden houden vond ik fijn.

## Bepaalde lange stukken uit app.py in helpers plaatsen

Ik heb er op het laatst voor gekozen om de onoverzichtelijkheid in app.py semi op te lossen door functies in helpers te zetten. 

Ik had eerst dat in app.py data met gebruik van de model classes functies werden aangeroepen, los van elkaar. Dat waren samen best veel losse functies.
Door meer losse functies in helpers te stoppen, is meeste onoverzichtelijkheid opgelost. De andere overzichtelijkheid zit hem meer in de database structuur. Ik had achteraf een table "lists" gemaakt, ipv table voor lists, watchlist en watched. Hierdoor zou mijn code overzichtelijker zijn en compacter.
