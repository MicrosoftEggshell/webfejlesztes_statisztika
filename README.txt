sok dependency, főleg bs4 és matplotlib (download_sites.py-nél wget $PATH-ban)

---

egy fájl futtatása előtt normális esetben egyszer le kell futtatni a felette lévőket is, de én most megtettem helyetted, használhatod rögtön a stats.py-t :)

	scrape_codes.py: összegyűjti az összes társértékelő kódot, elmenti codes.txt, forward_codes.json, backward,codes.json fájlokba
	|
	| - download_ratings.py: ertekelesek mappába letölti az összes oldalt, amin az értékelések vannak (style.css-t nem)
	|   |
	|   | - webdev_parser.py: kinyeri az adatokat az ertekelesek mappában lévő fájlokból és elmenti a crit_sites.pickle fájlba
	|   |   |
	|   |   | - stats.py: számok, adatok (crit_sites.pickle fájlból beolvasva); téged valószínűleg ez a fájl érdekel
	|
	| - download_sites.py: letölt MINDEN weboldalt (nem ajánlom a futtatását, főleg hogy van aki a 100mb limit háromszorosát is túllépte); system call van benne, windowson működik (de egyszerű átírni)

---

a classok methodjai többé-kevésbé magától adódó feladatokat látnak el, segítségért olvasd el a webdev_parser.py-t, vagy írd konzolba hogy `dir(ClassName)`, illetve `help(ClassName.method)`

pythonban a nem primitív válozók referencia szerint vannak tárolva, vagyis nyugodtan írhatok rekurzív adatszerkezeteket (pl. c : Criterion esetén c.ratings[0].criterion == c)

--
	forward_codes.json: dict, minden kulcs egy kód, minden érték egy lista azokkal a kódokkal, akiket a kulcs értékelt
	backward_codes.json: dict, minden kulcs egy kód, minden érték egy lista azokkal a kódokkal, akik a kulcsok értékelték