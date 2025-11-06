<<<<<<< HEAD
# Prog2-gruppuppgift

API:t ska använda JSON för all datakommunikation.

Det ska finnas endpoints för minst två av följande HTTP-metoder: GET, POST, PUT, DELETE.

Varje endpoint ska kunna ge korrekta HTTP-responskoder vid både framgång och fel, t.ex. 200 (OK), 422 (Unprocessable Entity), 404 (Not Found).

Felhantering kan ske manuellt eller med inbyggda verktyg.

API:t ska vara väl dokumenterat och kommenterat.

Folder structure for flask:
Skapa följande fil- och mappstruktur:

• application
    • __init__.py (Tom fil)
    • app.py (Tom fil)
• static
• templates
• tests
• docs
=======
# Group Project Test Website

This is a test web site for my group project.
>>>>>>> grupp_test/main


-------------------------------------------------------------------------------------------------
DevOps23 -Programmering 2 Nackademin Lärare: Dennis Rudin
Gruppuppgift
I denna uppgift skall ni bygga en lite mer detaljerad app. Ni skall använda minst ett externt API, men
gärna flera i kombination med varandra el. där resultatet av den ena ger information nödvändig för att
hämta den andra.

-------------------------------------------------------------------------------------------------
1 - Våran webbapp använder sig utan, Bootstrap + CSS ( för grundlayout), med hjälpa av AJAX och Jninja så kan vi
ha en "OnePageApp" där allting rendreas i bakgrunden. Vi har index.html som grund, och alla andra templates sätts 
i Jninja och hämtas med AJAX. 

UPPGIFT:
Applikationen skall ha ett front-end (webb-gränssnitt) och arbeta med en lite större datamängd, så
som statistisk data, eller annan form av register. Nedan är föreslaget Gutendex, vilken innehåller
information om alla böcker i Project Gutenberg (se nedan).
-------------------------------------------------------------------------------------------------

2 - Vi använder oss "cacheare" APIET från Elpriser, sparas dom lokalt så att vi kan återanvända dom.
Vi kan med hjälp utav Pandas och Plotly (alternativ JSON + CSS ) visa, jämföra, och optimera elpriser 
eller komsumption. 

UPPGIFT:
Bygg ett formulär för att kunna påverka sökresultatet på uppslagningen. Det finns 9 st olika parametrar
att påverka. Visa data i strukturerad form, gärna i tabellform med Pandas och kanske skicka någon
Pandas-kolumn till Plotly för att illustrera antal böcker eller annat som kan beräknas i ett diagram.
Visa informationen ni hämtat ur några olika perspektiv, t.ex lista per författare på en sida, medan ni
listar efter boktitlar på en annan. Pandas lämpar sig mycket bra till detta, dvs att ändra ordning på
data.
---------------------------------------------------------------------------------------------

3 - Applitationen tar nu cookies, tilldelar en UUID som är valid i 7 dagar.
- Med denna UUID kan vi också UTAN att registrera en användare använda "userinputdata" för 
sessioner under 7 dagar. det finns också endpoints som manipulerar tarbort eller skaper en ny! 

UPPGIFT:
Applikationen skall spara en Cookie när ni sökt med ert formulär (skickat en request). Innehållet i
denna är lite information (key-value) om den senaste sökningen. När ni sedan öppnar sidan med
formuläret igen läser ni denna cookie och fyller i några av sökfälten med hjälpa av jinja.
--------------------------------------------------------------------------------------------

4 - Vi har planerat vårt arbete med "Miro" och försökt hålla oss till en plan, det är inte alltid lika lätt som
man tänkt sig. Vi har då dokumenterat med hjälp utav kommentarer eller printscreens (Visa i powerpoint?)

EDIT --> Visa problemen vi stött på, förklara hur vi har tänkt, redovisa under demot och förklara vad som händer
samt varför vi gör på detta sätt.

UPPGIFT:
Anteckna under tiden ni bygger applikationen med saker ni upptäcker, t.ex problem som uppstått och
hur ni löst dem. Dessa anteckningar kan ni senare använda när ni skall presentera ert projekt under
vecka 45 som en inledning innan ni demonstrerar er applikation. Vi kan alla lära av varandras
erfarenheter, så detta kan bli en lärdom för andra även under presentationerna.
-------------------------------------------------------------------------------------------------

Vi har gjort några testcases men GÖR FLER! 

UPPGIFT:
Fundera över test case under tiden ni pratar om lösningar och skriv tester för de funktioner ni
skapar i appen. Tänk därför på att alla funktioner måste returnera något som går att testa.
Som i verkliga livet är det fritt att använda sig utav internet och alla tutorials som vi har använt i
studieplanen och under presentationer. Jag vill dock att ni undviker ChatGPT. I slutet av
presentationen från lektion sex finns en sida med titeln ”samlade tutorials”. Dessa skall innehålla allt
det vi gått igenom och som ni behöver för den här uppgiften.
Samarbeta för att hitta lösningar och alternativ.
-------------------------------------------------------------------------------------------------