# EcoHandel Partner Campaign - Follow-up Strategy

## Doel
Optimaliseren van engagement na de initiële campagne door gerichte follow-up mails, zonder duplicatie en met respect voor de leadstatus.

## Kernprincipes
1.  **Unieke Mails per Lead:** Nooit twee (identieke of te vergelijkbare) mails naar hetzelfde adres sturen binnen een korte periode, tenzij expliciet onderdeel van een geplande follow-up reeks met duidelijke inhoudelijke progressie.
2.  **Tracking is Leidend:** Opens, clicks en replies bepalen de follow-up actie.
3.  **Leadstatus is Cruciaal:** De status van een lead (geopend, geklikt, gereplied, ongeopend) bepaalt welke follow-up wordt verstuurd (of juist niet).

## Follow-up Plan

### Scenario 1: Lead heeft *niet* geopend (binnen 3-5 dagen)
-   **Inhoud:** Re-send van de originele mail (Variant A of B), maar met een **nieuwe subject line** die nieuwsgierigheid wekt of een ander voordeel benadrukt. Focus op de waarde van de Deye partnerprijslijst.
-   **Timing:** 3 dagen na eerste verzending.
-   **Doel:** Aandacht trekken en de eerste mail alsnog geopend krijgen.

### Scenario 2: Lead heeft *wel* geopend, maar *niet* geklikt of gereplied (binnen 5-7 dagen)
-   **Inhoud:** Korte, persoonlijke mail die inspeelt op het feit dat ze de eerste mail hebben gezien. Geen salespitch, maar een "soft touch" om de drempel te verlagen. Bijvoorbeeld: "Heb je onze Deye partnerprijslijst al kunnen bekijken? Ik wilde zeker weten dat je deze had ontvangen."
-   **Timing:** 5 dagen na eerste verzending.
-   **Doel:** Stimuleren van een klik naar de prijslijst of een reply.

### Scenario 3: Lead heeft *wel* geopend en *geklikt*, maar *niet* gereplied (binnen 7-10 dagen)
-   **Inhoud:** Meer specifieke follow-up die refereert aan de prijslijst. Bijvoorbeeld: "Ik zag dat je onze Deye partnerprijslijst hebt ingezien. Zijn er specifieke producten of vragen waar we je mee kunnen helpen?"
-   **Timing:** 7 dagen na de klik.
-   **Doel:** Conversatie starten of specifieke behoefte achterhalen.

### Scenario 4: Lead heeft *gereplied*
-   **Inhoud:** Human-in-the-loop opvolging door Milan/Tom. De agent signaleert de reply en voegt dit toe aan het Hot Prospects rapport.
-   **Timing:** Direct na ontvangst van de reply.
-   **Doel:** Persoonlijke sales opvolging.

## Tracking & Automatisering
-   De lokale SQLite database blijft de bron van waarheid voor de status van elke lead en welke mail er is verstuurd (en wanneer).
-   De `run_daily_cycle.py` script wordt uitgebreid om automatisch te controleren op follow-up triggers op basis van bovenstaande scenario's.
-   Nieuwe follow-up campagnes worden aangemaakt in Brevo met unieke campaign keys en onderwerpen, gelinkt aan de originele batch.

## Rapportage
-   Het Hot Prospects rapport wordt uitgebreid met aanbevelingen voor follow-up mails, inclusief het scenario en de voorgestelde actie.

Dit plan zal worden geïmplementeerd en bijgehouden om de effectiviteit van de campagne continu te verbeteren.
