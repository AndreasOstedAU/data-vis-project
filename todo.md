## Dette er en knap så tom to-do liste

To do:

- Find problemer med data og fiks dem
- Check dem hvor der er unknown-skewed distribution
 - Hvad gør vi med unknown og når alder er 0 og 1?
	- Andre værdier som er urealistiske?
-[OK] Lav legend så farvene altid er til den samme værdi (open: rød)
- Lav barchart til antal mord per år
- Integrer sankey diagram og tids-spiral plot 
	- Sankey skal kun opdatere på city selection
- Find bedste arrangement af figurer 
- [OK] Normaliser med antal år i data for hver by også (Andreas)
- Lav hoverdata pæn (alle figurer) og beslut hvilken information der skal vises
- Juster zoom-niveau ved valg af city
- [OK] Sortering af barchart (alfabetisk)
- Figurer hvis der ikke er noget data i filtrering (ideelt kort hvor der står "No data")
- [OK] **Opdater colorscale på spiral plot med task-driven color coding (histogram equalization)**
- [OK] Evt. filtering af andre plots ved klik på spiral plot


Klaret:

- Få styr på målgruppe
- Tid på mordet?
- (Clara) Lav en knap pr by, hvor man så zoomer ind på byen
	- Dette skal også ændre de andre plots i dashboardet
- Kombiner klik og filter, så filteret opdaterer når man klikker på graferne, f.eks. Hvis vi klikker på "Asian", så skal filteret skiftes til "Asian"
- (Andreas) Opdater zoom på aktuel kortvisning (by eller hele USA)
- Få fat i indbyggertal i byerne (Clara)
- Lav prikker forskellige størrelser at efter antal af mord
	- Normaliseret efter indbyggertal (Clara)
- Lav det sådan at de andre grafer opdaterer når man markerer punkter
- Skal vi have noget andet som farver på kortet (nej)