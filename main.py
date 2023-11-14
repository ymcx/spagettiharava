from datetime import date, datetime
import haravasto as h
import webbrowser
import random
import pyglet
import time

m = {                       # Muuttujat
    "txnaatit": [[], []],   # Aloitusvalikon testikentän x:ien koordinaatit
    "vnappula": [0, 1],     # Aloitusvalikon asetusten viimeiseksi painettu nappula
    "siirtoja": 0,          # Tehtyjen siirtojen lukumäärä
    "gfreimi":  7,          # Tulosruudun GIF:n freimi
    "pkentta":  [],         # Piirrettävä kenttä
    "miinoja":  10,         # Kentällä olevien miinojen lukumäärä
    "kentta":   [],         # Oikea kenttä miinoineen yms.
    "varit":    [(), ""],   # Taustojen ja ruutujen värit
    "lsana":    "",         # Tulosruudulle liitetty voittoa/häviötä kuvaava sana
    "kdim":     [9, 9],     # Kentän dimensiot (korkeus x leveys)
    "aika":     0,          # Pelin aloitusaika
    "kk":       40,         # Ruutujen tekstuurien kuvakoko
}

def universaali_nappain_kasittelija(symboli, _):
    if symboli in [65293, 32, 121]:         # Painettiin Enteriä, Spacea tai Y:tä
        if m["varit"][1] == "c1":           # Ollaan aloitusvalikossa
            h.lopeta()
            peli()
        elif m["varit"][1] in ["c2", "c3"]: # Ollaan tulosruudussa (hävitty tai voitettu)
            tulosruutu_uudelleenpeluu()

    elif symboli in [65307, 65288, 110]:    # Painettiin Esc:iä, Backspacea tai N:ää
        h.lopeta()

def aloitusvalikko_naattigeneraattori():
    m["txnaatit"] = [[], []]                    # Tyhjennetään edelliset koordinaatit
    for i in range(round( m["miinoja"] / 5 )):  # Asioita tapahtuu...
        for j in range(2):                      # Trust me, spagettipyramidi vaan toimii
            m["txnaatit"][j].append(
                m["kk"] * (
                    2.5 + 4*j - 0.5*m["vnappula"][0] + 0.1*random.randrange(
                        10 * round(
                            m["kdim"][1] ** 0.5
                        )
                    )
                )
            )

def aloitusvalikko_piirto():
    h.tyhjaa_ikkuna()
    h.piirra_tausta()
    h.aloita_ruutujen_piirto()

    # Taustaruudut
    leveys = 17
    for i in range(145):
        h.lisaa_piirrettava_ruutu(
            m["varit"][1],
            m["kk"] * (i*2%leveys),
            m["kk"] * int(i*2/leveys)
        )

    # Logo
    h.lisaa_piirrettava_ruutu(
        "c4",                           # c4 = Logo
        m["kk"] * 7.5,
        m["kk"] * 5.75
    )

    # Tekstinappuloiden taustaruudut
    nappulat = [
        # Ruutu X, Ruutu Y, Laatikon pituus, Tekstuuri, Sana,       Tekstin X, Tekstin Y
        (1.5,      14.5,    8,               " ",       "HAASTE",   2.5,       14.5),
        (1.5,      12.5,    8,               " ",       "KOKO",     3.5,       12.5),
        (1.5,      3.5,     6,               "0",       "LOPETA",   1.5,       3.5 ),
        (8.5,      3.5,     7,               "0",       "PELAA",    9.5,       3.5 ),
        (1.5,      1.5,     14,              "0",       "TILASTOT", 4.5,       1.5 ),
    ]
    for i in range(len(nappulat)):
        for j in range(nappulat[i][2]):
            h.lisaa_piirrettava_ruutu(
                nappulat[i][3],
                m["kk"] * (nappulat[i][0]+j),
                m["kk"] * nappulat[i][1]
            )

    # Testikentän tyhjät ruudut
    testikentta_koko = int( 1 + m["kdim"][1] ** 0.5 )
    for i in range(testikentta_koko):
        for j in range(testikentta_koko):
            h.lisaa_piirrettava_ruutu(
                " ",
                m["kk"] * (j+2.5-0.5*m["vnappula"][0]),
                m["kk"] * (i+6.5-0.5*m["vnappula"][0])
            )

    # Testikentän X ruudut
    for i in range(round( m["miinoja"] / 5 )):
        h.lisaa_piirrettava_ruutu(
            "x",
            m["txnaatit"][0][i],
            m["txnaatit"][1][i]
        )

    # Asetusnappulat (vaikeus & kenttäkoko)
    for i in range(6):
        h.lisaa_piirrettava_ruutu(
            str(i%3+1),
            m["kk"] * (10.5+i%3*2),
            m["kk"] * (14.5-int(i/3)*2)
        )

    # Valittujen asetusnappuloiden korostus
    for i in range(2):
        h.lisaa_piirrettava_ruutu(
            "f",
            m["kk"] * (10.5+2*m["vnappula"][i]),
            m["kk"] * (12.5+2*i)
        )

    h.piirra_ruudut()

    # Tekstinappuloiden tekstit
    for i in range(len(nappulat)):
        for j in range(len(nappulat[i][4])):
            h.piirra_tekstia(
                nappulat[i][4][j],
                m["kk"] * (nappulat[i][5]+j) + 11,
                m["kk"] * nappulat[i][6] + 4,
                (53, 53, 53, 255),
                "arial",
                20
            )

def aloitusvalikko_hiiri(x, y, nappula, _):
    # 'if else if else if' -viidakkoa näkyvissä!
    if nappula == 1:
        nappula_vaihtunut = False

        # Kenttäkokonapit
        if m["kk"]*12.5 < y < m["kk"]*13.5:
            if m["kk"]*10.5 < x < m["kk"]*11.5:     # 1. Nappula, kentän dimensiot ovat 9x9
                m["kdim"][0] = 9
                m["kdim"][1] = 9
                if m["vnappula"][0] != 0:           # Jos ei viimeksi olla painettu kyseistä
                    nappula_vaihtunut = True        # nappulaa, niin siirrä korostus siihen
                    m["vnappula"][0] = 0            # ja anna signaali painetusta nappulasta
            elif m["kk"]*12.5 < x < m["kk"]*13.5:   # 2., 16x16
                m["kdim"][0] = 16
                m["kdim"][1] = 16
                if m["vnappula"][0] != 1:
                    nappula_vaihtunut = True
                    m["vnappula"][0] = 1
            elif m["kk"]*14.5 < x < m["kk"]*15.5:   # 3., 16x30
                m["kdim"][0] = 16
                m["kdim"][1] = 30
                if m["vnappula"][0] != 2:
                    nappula_vaihtunut = True
                    m["vnappula"][0] = 2

        # Vaikeusastenapit
        elif m["kk"]*14.5 < y < m["kk"]*15.5:
            if m["kk"]*10.5 < x < m["kk"]*11.5 and m["vnappula"][1] != 0:   # 1., Miinat x 0.5
                nappula_vaihtunut = True
                m["vnappula"][1] = 0
            elif m["kk"]*12.5 < x < m["kk"]*13.5 and m["vnappula"][1] != 1: # 2., Miinat x 1
                nappula_vaihtunut = True
                m["vnappula"][1] = 1
            elif m["kk"]*14.5 < x < m["kk"]*15.5 and m["vnappula"][1] != 2: # 3., Miinat x 1.5
                nappula_vaihtunut = True
                m["vnappula"][1] = 2

        elif m["kk"]*3.5 < y < m["kk"]*4.5:
            if m["kk"]*1.5 < x < m["kk"]*7.5:       # Sulje spagettiharava  :'(
                h.lopeta()
            elif m["kk"]*8.5 < x < m["kk"]*15.5:    # Aloita peli           :')
                h.lopeta()
                peli()

        # Tilastonappula (avautuu selaimessa, koska en löytänyt
        # fiksua keinoa avata tiedostoa oletustekstieditorissa)
        elif m["kk"]*1.5 < y < m["kk"]*2.5 and m["kk"]*1.5 < x < m["kk"]*15.5:
            webbrowser.open("tilastot.txt")

        # On aika laskea miinojen lukumäärä kenttäkoon perusteella !
        if nappula_vaihtunut:                                   # Vaikeustaso:     1  2   3
            match m["kdim"][1]:
                case 9:                                         # Miinoja (9x9):   5  10  15
                    m["miinoja"] = 5 * (m["vnappula"][1]+1)
                case 16:                                        # Miinoja (16x16): 20 40  60
                    m["miinoja"] = 20 * (m["vnappula"][1]+1)
                case 30:                                        # Miinoja (16x30): 50 100 150
                    m["miinoja"] = 50 * (m["vnappula"][1]+1)
            aloitusvalikko_naattigeneraattori()                 # Päivitetään testikenttä

def lataa_custom_spritet():
    pyglet.resource.path = ["uwu"]
    kuvat = {}
    kuvat["0"] = pyglet.resource.image("ruutu_tyhja.png")
    for i in range(1, 9):
        kuvat[str(i)] = pyglet.resource.image("ruutu_{}.png".format(i))
    for i in range(1, 10):
        kuvat["c" + str(i)] = pyglet.resource.image("{}.png".format(i))
    kuvat["x"] = pyglet.resource.image("ruutu_miina.png")
    kuvat[" "] = pyglet.resource.image("ruutu_selka.png")
    kuvat["f"] = pyglet.resource.image("ruutu_lippu.png")
    h.grafiikka["kuvat"].update(kuvat)

def aloitusvalikko():
    lataa_custom_spritet()
    m["varit"][0] = (220, 186, 127, 255)                        # Keltainen tausta
    m["varit"][1] = "c1"                                        # c1 = Keltainen ruutu
    h.grafiikka["taustavari"] = m["varit"][0]
    h.luo_ikkuna(m["kk"]*17, m["kk"]*17, m["varit"][0])
    aloitusvalikko_naattigeneraattori()
    h.aseta_nappain_kasittelija(universaali_nappain_kasittelija)
    h.aseta_piirto_kasittelija(aloitusvalikko_piirto)
    h.aseta_hiiri_kasittelija(aloitusvalikko_hiiri)
    h.aloita()

def peli_hiiri(x, y, nappula, _):
    y_tmp = m["kdim"][0] - int(y/m["kk"]) - 1   # Kuvataan absoluuttiset koordinaatit
    x_tmp = int(x/m["kk"])                      # ruutukoordinaattien virittämän
                                                # vektoriavaruuden suhteen
    if 0 <= x_tmp < m["kdim"][1] and 0 <= y_tmp < m["kdim"][0]:
        match nappula:
            case 1:
                peli_ruudun_avaus(y_tmp, x_tmp)        # Avataan painettu ruutu
            case 4:
                peli_liputus(y_tmp, x_tmp)      # Liputetaan painettu ruutu

    tyhja_lkm = 0
    for rivi in m["pkentta"]:                   # Lasketaan tyhjien ruutujen lukumäärä
        for alkio in rivi:
            if alkio in [" ", "f", "x"]:
                tyhja_lkm += 1

    if tyhja_lkm == m["miinoja"]:               # Jos tyhjien ruutujen lukumäärä on
        m["lsana"] = "VOITIT PELIN!"            # sama kuin miinojen lukumäärä, on
        m["varit"][0] = (192, 245, 149, 255)    # pelaaja voittanut pelin
        m["varit"][1] = "c3"                    # c3 = Vihreä ruutu
        peli_lopetus("f")                       # Liputetaan vielä kaikki miinat
                                                # ja aloitetaan pelin lopetus
def peli_lopetus(merkki):
    for i in range( m["kdim"][0] * m["kdim"][1] ):
        y = int( i / m["kdim"][1] )
        x = int( i % m["kdim"][1] )
        if m["kentta"][y][x] == "x":
            m["pkentta"][y][x] = merkki
    h.aseta_hiiri_kasittelija(peli_jaadytys)        # Estä pelaajaa tekemästä siirtoja
    h.aseta_toistuva_kasittelija(peli_suljenta, 1)  # pelin loputtua... grr

def peli_suljenta(_):
    h.lopeta()
    file = open("tilastot.txt", "a")                # Kirjoita statistiikat muistiin
    file.write(
        f"siirtoja     : {m['siirtoja']}\n"
        f"miinoja      : {m['miinoja']}\n"
        f"kenttä (k/l) : {str(m['kdim'][0])}x{str(m['kdim'][1])}\n"
        f"status       : {m['lsana']}\n"
        f"kesto  (m)   : {round( (time.time()-m['aika']) / 60, 2 )}\n"
        f"pvm          : {date.today()}\n"
        f"klo          : {datetime.now().hour}:{datetime.now().minute}\n\n"
    )
    file.close()
    tulosruutu()                                    # Pelin loputtua avaa tulosruutu

def peli_jaadytys(*_):
    pass

def peli_liputus(y, x):
    if m["pkentta"][y][x] == " ":                   # Jos tyhjä, liputa
        m["pkentta"][y][x] = "f"
    elif m["pkentta"][y][x] == "f":
        m["pkentta"][y][x] = " "                    # Jos lippu, tyhjätä

def peli_miinoitus():
    naattilista = list(range( 0, m["kdim"][0] * m["kdim"][1] ))
    random.shuffle(naattilista)                     # Sekoita naattilistaa miinojen
    for i in range(m["miinoja"]):                   # satunnaiselle asettamiselle
        y = int( naattilista[i] / m["kdim"][1] )
        x = naattilista[i] % m["kdim"][1]
        m["kentta"][y][x] = "x"                     # Aseta ruutuun miina ja laita
        for i in range(9):                          # sen viereen numeroruudut
            y_tmp = y - 1 + int(i/3)
            x_tmp = x - 1 + i % 3                   # \/ Varmista tarkistuksen laillisuus
            if 0 <= x_tmp < m["kdim"][1] and 0 <= y_tmp < m["kdim"][0]:
                try:                                # Korota numeroa, jos ruutu on numerollinen
                    m["kentta"][y_tmp][x_tmp] = str( 1 + int(m["kentta"][y_tmp][x_tmp]) )
                except ValueError:                  # Numeroi ruutu, jos se ei ole numerollinen
                    if m["kentta"][y_tmp][x_tmp] == " ":
                        m["kentta"][y_tmp][x_tmp] = "1"

def peli_ruudun_avaus(y, x):
    m["siirtoja"] += 1                              # Kukaan näitä kommentteja muutenkaan lue
    if m["pkentta"][y][x] != "f":
        match m["kentta"][y][x]:
            case "x":
                m["lsana"] = "HÄVISIT PELIN!"
                m["varit"][0] = (239, 102, 103, 255)
                m["varit"][1] = "c2"
                peli_lopetus("x")

            case " ":
                tutkittava = [[y, x]]
                while tutkittava:
                    y_eka = tutkittava[0][0]
                    x_eka = tutkittava[0][1]
                    m["pkentta"][y_eka][x_eka] = "0"
                    for i in range(9):
                        y_tmp = y_eka - 1 + int(i/3)
                        x_tmp = x_eka - 1 + i%3
                        if 0 <= x_tmp < m["kdim"][1] and 0 <= y_tmp < m["kdim"][0]:
                            if m["kentta"][y_tmp][x_tmp] == " " and m["pkentta"][y_tmp][x_tmp] != "0":
                                tutkittava.append([y_tmp, x_tmp])
                            elif m["kentta"][y_tmp][x_tmp] not in ["x", " "]:
                                m["pkentta"][y_tmp][x_tmp] = m["kentta"][y_tmp][x_tmp]
                    # https://stackoverflow.com/questions/1157106/
                    tutkittava = [i for i in tutkittava if i != tutkittava[0]]

            case _:
                m["pkentta"][y][x] = m["kentta"][y][x]

def peli_piirto():
    h.tyhjaa_ikkuna()
    h.piirra_tausta()

    for rivi in range(m["kdim"][0]):
        for sarake in range(m["kdim"][1]):
            h.lisaa_piirrettava_ruutu(
                m["pkentta"][rivi][sarake],
                m["kk"] * sarake,
                m["kk"] * (m["kdim"][0]-rivi-1)
            )

    h.piirra_ruudut()

def peli():
    m["pkentta"] = []
    m["kentta"] = []
    for rivi in range(m["kdim"][0]):
        m["pkentta"].append([])
        m["kentta"].append([])
        for sarake in range(m["kdim"][1]):
            m["pkentta"][-1].append(" ")
            m["kentta"][-1].append(" ")

    m["varit"][1] = " "
    peli_miinoitus()
    m["aika"] = time.time()
    h.luo_ikkuna(m["kk"]*m["kdim"][1], m["kk"]*m["kdim"][0])
    h.aseta_piirto_kasittelija(peli_piirto)
    h.aseta_hiiri_kasittelija(peli_hiiri)
    h.aloita()

def tulosruutu_uudelleenpeluu():
    h.lopeta()
    aloitusvalikko()

def tulosruutu_toisto(_):
    m["gfreimi"] = m["gfreimi"] % 3 + 7

def tulosruutu_piirto():
    h.tyhjaa_ikkuna()
    h.piirra_tausta()

    # Taustaruudut
    leveys = 17
    for i in range( leveys * 17 ):
        h.lisaa_piirrettava_ruutu(
            m["varit"][1],
            m["kk"] * (i%leveys+int(i%2)),
            m["kk"] * int(i/leveys)
        )

    # Pelinjatkamisnappulat
    for i in range(2):
        h.lisaa_piirrettava_ruutu(
            f"c{str(i+5)}",
            m["kk"] * (12.5+2*i),
            m["kk"] * 8.5
        )

    # Nappuloiden taustaruudut
    for i in range(2):
        for j in range(10+i*4):
            h.lisaa_piirrettava_ruutu("0", m["kk"]*(j+1.5), m["kk"]*(8.5+i*2))

    # Kolmio ukko gif :D
    # Ompa hyvä :DD
    h.lisaa_piirrettava_ruutu(f"c{str(m['gfreimi'])}", m["kk"]*11.5,  m["kk"]*11.25)

    h.piirra_ruudut()

    # Tekstit
    sanat = [m["lsana"], "UUDESTAAN?"]
    for i in range(len(sanat)):
        for j in range(len(sanat[i])):
            h.piirra_tekstia(
                sanat[i][j],
                m["kk"] * (1.5+j) + 11,
                m["kk"] * (10.5-2*i) + 4,
                (53, 53, 53, 255),
                "arial",
                20
	    )

def tulosruutu_hiiri(x, y, nappula, _):
    if nappula == 1 and m["kk"]*8.5 < y < m["kk"]*9.5:
        if m["kk"]*12.5 < x < m["kk"]*13.5:
            tulosruutu_uudelleenpeluu()
        elif m["kk"]*14.5 < x < m["kk"]*15.5:
            h.lopeta()

def tulosruutu():
    h.grafiikka["taustavari"] = m["varit"][0]
    h.luo_ikkuna(m["kk"]*17, m["kk"]*17)
    h.aseta_toistuva_kasittelija(tulosruutu_toisto, 1/2)
    h.aseta_piirto_kasittelija(tulosruutu_piirto)
    h.aseta_hiiri_kasittelija(tulosruutu_hiiri)
    h.aloita()

if __name__ == "__main__":
    aloitusvalikko()
