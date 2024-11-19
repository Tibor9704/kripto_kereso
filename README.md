1. Áttekintés

Ez a dokumentáció a Kriptovaluta Kereső alkalmazás telepítésének, konfigurálásának és futtatásának részleteit tartalmazza. Az alkalmazás célja, hogy kriptovaluták aktuális árfolyamait jelenítse meg, 24 órás adatokkal kiegészítve, valamint az árfolyamváltozások alapján a csökkent és emelkedett értékű valutákat listázza. Az egyénileg keresett illetve listában lekért adatok adatbázis táblákban eltárolódnak.

2. Rendszerkövetelmények

Szerver követelmények:
Operációs rendszer: Linux vagy Windows
Python: 3.8 vagy újabb
MySQL: 8.0 vagy újabb
Internetkapcsolat (az API-hívásokhoz)

Telepítendő Python csomagok:
A szükséges csomagokat a requirements.txt fájl tartalmazza. 

Telepítésük:
pip install -r requirements.txt

Főbb csomagok:
Flask: Webalkalmazás keretrendszer.
mysql-connector-python: MySQL adatbázis kapcsolat kezelésére.
plotly: Interaktív grafikonok megjelenítésére.
requests: API hívásokhoz.

3. Adatbázis Beállítások

Hozz létre egy új MySQL adatbázist a database.txt segítségével.

4. Alkalmazás Futtatása

Indítsd el az alkalmazást:
python app.py
Az alkalmazás alapértelmezett elérhetősége: http://127.0.0.1:5000

5. Fő Funkciók
   
Árfolyam Keresés:
Írj be egy kriptovalutát (pl. BTC), és megkapod az aktuális árfolyamot USD-ben.
A 24 órás árfolyam történet grafikonon jelenik meg.

Véletlenszerű árfolyamok:
Az alkalmazás véletlenszerűen 5 kriptovalutát jelenít meg az árfolyamukkal és százalékos változásukkal.

Top 10 nyereséges/veszteséges:
Kattints az Emelkedett vagy Zuhant gombokra, hogy megjelenítsd a legnagyobb árfolyam-növekedést vagy csökkenést mutató valutákat.
