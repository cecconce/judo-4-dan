#!/usr/bin/env python3
"""Genera assets/quiz.json: banco di domande a 4 risposte, per capitolo.

Ogni domanda: {"t": id capitolo, "q": testo, "o": [4 opzioni, la PRIMA è la corretta], "e": spiegazione}.
Il mescolamento delle opzioni avviene nel browser (assets/quiz.js).
Parte delle domande è generata dalle tabelle dei capitoli (Gokyo, glossario, Kime, Goshin),
parte è scritta a mano dal testo dei capitoli: ogni spiegazione cita il capitolo.
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).parent
rnd = random.Random(4)  # seme fisso: output riproducibile
Q = []


def clean(s):
    return re.sub(r"\s+", " ", s.replace("*", "").replace("`", "")).strip()


def tables(text):
    """Restituisce le tabelle markdown come liste di righe (liste di celle, senza intestazione)."""
    out, cur = [], []
    for line in text.splitlines():
        if line.strip().startswith("|"):
            cells = [clean(c) for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) or c == "" for c in cells) and any(cells):
                continue
            cur.append(cells)
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def add(t, q, correct, wrong, e):
    wrong = [w for w in dict.fromkeys(wrong) if w != correct]
    assert len(wrong) >= 3, (q, wrong)
    Q.append({"t": t, "q": q, "o": [correct] + wrong[:3], "e": e})


def pick(pool, exclude, n=3):
    pool = [p for p in dict.fromkeys(pool) if p not in exclude]
    rnd.shuffle(pool)
    return pool[:n]


def read(name):
    return (ROOT / "content" / name).read_text(encoding="utf-8")


def chap(prefix):
    return next((ROOT / "content").glob(prefix + "-*.md"))


# ---------------------------------------------------------------- Gokyo (cap. 5-9) dalle tabelle del cap. 4
GRUPPI = ["Dai-ikkyō (1° gruppo)", "Dai-nikyō (2° gruppo)", "Dai-sankyō (3° gruppo)", "Dai-yonkyō (4° gruppo)", "Dai-gokyō (5° gruppo)"]
c4 = read(chap("04").name)
gtabs = [t for t in tables(c4) if t[0] == ["#", "Tecnica", "Kanji", "Famiglia"]]
assert len(gtabs) == 5, len(gtabs)
all_fam = []
all_kanji = []
for tb in gtabs:
    for r in tb[1:]:
        all_fam.append(r[3])
        all_kanji.append(r[2])
for gi, tb in enumerate(gtabs):
    t = f"{5 + gi:02d}"
    rows = tb[1:]
    names = [r[1] for r in rows]
    for n, name, kanji, fam in rows:
        src = f"Cap. 4 (classificazione): {name} ({kanji}) è la tecnica n. {n} del {GRUPPI[gi]}, famiglia {fam}."
        add(t, f"A quale famiglia appartiene {name} secondo la classificazione Kōdōkan?", fam,
            pick(sorted(set(all_fam)), [fam]), src)
        add(t, f"Quale kanji corrisponde a {name}?", kanji, pick(all_kanji, [kanji]), src)
        add(t, f"Nel {GRUPPI[gi].split(' (')[0]}, quale tecnica occupa la posizione n. {n}?", name,
            pick(names, [name]), src)

# ---------------------------------------------------------------- Glossario (cap. 12)
gl = [r for r in tables(read(chap("12").name))[0][1:] if "/" not in r[0] and "Osae" not in r[0]]
meanings = [r[2] for r in gl]
for term, kanji, mean in gl:
    add("12", f"Che cosa significa «{term}»?", mean, pick(meanings, [mean]),
        f"Cap. 12 (glossario): {term} ({kanji}) = {mean}.")

# ---------------------------------------------------------------- Kime no Kata (cap. 13) dalla tabella «Struttura del kata»
c13 = read(chap("13").name)
kt = next(t for t in tables(c13) if t[0][:3] == ["N.", "Serie", "Nome"])[1:]
k_names = [re.sub(r"\s*\(.*\)", "", r[2]) for r in kt]
k_att = [r[4] for r in kt]
assert len(kt) == 20
for r in kt:
    n, serie, nome = r[0], r[1], re.sub(r"\s*\(.*\)", "", r[2])
    src = f"Cap. 13 (struttura del kata): n. {n} {serie} — {nome}: Uke {r[4]}; Tori: {r[5]}."
    add("13", f"Quale tecnica è la n. {n} del Kime no Kata?", f"{nome} ({serie})",
        pick([f"{x} ({kt[i][1]})" for i, x in enumerate(k_names)], [f"{nome} ({serie})"]), src)
    add("13", f"Nel Kime no Kata, che attacco porta Uke in {nome} ({serie})?", r[4], pick(k_att, [r[4]]), src)

# ---------------------------------------------------------------- Goshin-jutsu (cap. 14) dalle tabelle 2.2 e 2.3
c14 = read(chap("14").name)
tb = tables(c14)
toshu = next(t for t in tb if t[0][:3] == ["N.", "Nome", "Kanji"] and t[0][3] == "Attacco")[1:]
buki = next(t for t in tb if t[0][:3] == ["N.", "Nome", "Kanji"] and t[0][3] == "Arma")[1:]
assert len(toshu) == 12 and len(buki) == 9, (len(toshu), len(buki))
t_names = [r[1] for r in toshu]
t_kanji = [r[2] for r in toshu]
t_att = [r[3] for r in toshu]
for r in toshu:
    src = f"Cap. 14, tab. 2.2 (Toshu no bu): n. {r[0]} {r[1]} ({r[2]}) — attacco: {r[3]}."
    add("14", f"Quale tecnica è la n. {r[0]} del Toshu no bu (mani nude) del Goshin-jutsu?", r[1], pick(t_names, [r[1]]), src)
    add("14", f"Quale kanji corrisponde a {r[1]} (Toshu no bu)?", r[2], pick(t_kanji, [r[2]]), src)
    add("14", f"Nel Goshin-jutsu, quale attacco subisce Tori in {r[1]}?", r[3], pick(t_att, [r[3]]), src)
b_names = [r[1] for r in buki]
b_kanji = [r[2] for r in buki]
for r in buki:
    src = f"Cap. 14, tab. 2.3 (Buki no bu): n. {r[0]} {r[1]} ({r[2]}) — arma: {r[3]}."
    add("14", f"Quale tecnica è la n. {r[0]} del Buki no bu (armi) del Goshin-jutsu?", r[1], pick(b_names, [r[1]]), src)
    add("14", f"Quale kanji corrisponde a {r[1]} (Buki no bu)?", r[2], pick(b_kanji, [r[2]]), src)

# ---------------------------------------------------------------- Memorizzazione (cap. 17): ordine delle tecniche
for i in range(len(k_names) - 1):
    add("17", f"Nel Kime no Kata, quale tecnica segue {k_names[i]} (n. {i + 1})?", k_names[i + 1],
        pick(k_names, [k_names[i], k_names[i + 1]]),
        f"Cap. 13/17: l'ordine del Kime no Kata è fisso; dopo n. {i + 1} {k_names[i]} viene n. {i + 2} {k_names[i + 1]}.")
for i in range(len(t_names) - 1):
    add("17", f"Nel Toshu no bu del Goshin-jutsu, quale tecnica segue {t_names[i]} (n. {i + 1})?", t_names[i + 1],
        pick(t_names, [t_names[i], t_names[i + 1]]),
        f"Cap. 14/17: dopo n. {i + 1} {t_names[i]} viene n. {i + 2} {t_names[i + 1]}.")
for i in range(len(b_names) - 1):
    add("17", f"Nel Buki no bu del Goshin-jutsu, quale tecnica segue {b_names[i]} (n. {i + 1})?", b_names[i + 1],
        pick(b_names, [b_names[i], b_names[i + 1]]),
        f"Cap. 14/17: dopo n. {i + 1} {b_names[i]} viene n. {i + 2} {b_names[i + 1]}.")
add("17", "Come si ripartiscono le 20 tecniche del Kime no Kata?", "8 Idori (in ginocchio) e 12 Tachiai (in piedi)",
    ["12 Idori e 8 Tachiai", "10 Idori e 10 Tachiai", "5 Idori e 15 Tachiai"], "Cap. 13/17: Idori 8 (n. 1–8), Tachiai 12 (n. 9–20).")
add("17", "Come si ripartiscono le 21 tecniche del Kōdōkan Goshin-jutsu?", "12 Toshu no bu (mani nude) e 9 Buki no bu (armi)",
    ["9 Toshu no bu e 12 Buki no bu", "10 Toshu no bu e 11 Buki no bu", "14 Toshu no bu e 7 Buki no bu"], "Cap. 14/17: 12 + 9 = 21.")

# ---------------------------------------------------------------- Domande scritte a mano, dal testo dei capitoli
H = []


def h(t, q, correct, wrong, e):
    H.append((t, q, correct, wrong, e))


# 01 Storia
h("01", "In che anno e dove Kanō Jigorō fondò il Kōdōkan?", "1882, nel tempio Eishō-ji a Tokyo (quartiere di Shitaya)",
  ["1877, nel dojo dell'Università Imperiale", "1883, nel tempio Eishō-ji", "1895, al Butokukai di Kyōto"], "Cap. 1, §1.2: maggio 1882, sala di dodici tatami con nove allievi.")
h("01", "Quali furono i primi due cintura nera della storia, promossi nel 1883?", "Tomita Tsunejirō e Saigō Shirō",
  ["Yamashita Yoshitsugu e Koizumi Gunji", "Mifune Kyūzō e Tani Yukio", "Iikubo Tsunetoshi e Iso Mataemon"], "Cap. 1, §1.2: nel 1883 Kanō introdusse il sistema dan/kyū.")
h("01", "Da quale gioco Kanō mutuò il sistema dei gradi dan/kyū?", "Il gioco del go", ["Gli scacchi giapponesi (shōgi)", "Il kendō", "Il sumō"], "Cap. 1, §1.2.")
h("01", "Quali due scuole di jūjutsu studiò Kanō per costruire il judo?", "Tenjin Shin'yō-ryū e Kitō-ryū",
  ["Totsuka-ha Yōshin-ryū e Kitō-ryū", "Tenjin Shin'yō-ryū e Daitō-ryū", "Takenouchi-ryū e Kitō-ryū"], "Cap. 1, §1.1: la prima per atemi e katame-waza, la seconda per nage-waza e randori.")
h("01", "Quando morì Kanō Jigorō, e dove?", "Il 4 maggio 1938, a bordo dell'Hikawa Maru",
  ["Il 4 maggio 1938, a Tokyo", "Il 28 ottobre 1938, a Kobe", "Il 4 maggio 1945, a Mikage"], "Cap. 1, §1.2: tornava dalla sessione CIO del Cairo; era nato il 28 ottobre 1860 a Mikage.")
h("01", "Quando Kanō fissò le massime Seiryoku Zen'yō e Jita Kyōei con la Società Culturale del Kōdōkan?", "1922", ["1882", "1895", "1938"], "Cap. 1, §1.3 e cap. 2.")
h("01", "Dove e quando fu fondato il Budokwai, più antico club di judo fuori dal Giappone?", "A Londra, il 26 gennaio 1918, da Koizumi Gunji",
  ["A Londra, nel 1899, da Tani Yukio", "A Seattle, nel 1903, da Yamashita Yoshitsugu", "A Parigi, nel 1920, da Kanō"], "Cap. 1, §1.4.")
h("01", "Quando nacque la IJF (International Judo Federation)?", "L'11-12 luglio 1951, a Londra", ["Il 28 luglio 1948, a Londra", "Nel 1964, a Tokyo", "Nel 1960, a Roma"], "Cap. 1, §1.4: la EJU era stata rifondata a Londra il 28 luglio 1948.")
h("01", "In quale edizione dei Giochi olimpici esordì il judo maschile?", "Tokyo 1964", ["Roma 1960", "Tokyo 1940", "Mosca 1980"], "Cap. 1, §1.4: ammesso nella sessione CIO di Roma dell'agosto 1960.")
h("01", "Kanō Jigorō divenne nel 1909 un membro particolare del CIO: quale?", "Il primo membro asiatico della storia del CIO", ["Il primo presidente del CIO", "Il primo giapponese medaglia d'oro", "Il fondatore dei Giochi del 1940"], "Cap. 1, §1.4.")
h("01", "Quando e dove fu fondata la Federazione Jiu-Jitsuista Italiana (FJJI)?", "Il 30 marzo 1924 a Roma, da ventotto società",
  ["Il 18 gennaio 1902 a Milano", "Il 1° luglio 2000 a Ostia", "Il 29 marzo 1981 a Roma"], "Cap. 1, §1.5.")
h("01", "Quante medaglie olimpiche ha vinto il judo italiano (dato del manuale) e quanti ori?", "19 medaglie, di cui 5 ori", ["12 medaglie, di cui 3 ori", "25 medaglie, di cui 8 ori", "19 medaglie, di cui 2 ori"], "Cap. 1, §1.5: da verificare dopo le ultime Olimpiadi.")
h("01", "Quale tecnica era legata alla vittoria leggendaria di Saigō Shirō su Terushima Tarō?", "Yama-arashi (山嵐)", ["Uchi-mata", "Tomoe-nage", "Seoi-nage"], "Cap. 1, §1.3: episodio di tradizione; lo yama-arashi non è nella nomenclatura ufficiale.")

# 02 Filosofia
h("02", "Che cosa significa Ju-no-ri (柔の理)?", "Principio della cedevolezza", ["Principio della prosperità reciproca", "Massimo uso dell'energia", "Via dell'etichetta"], "Cap. 2, §2.1.")
h("02", "Che cosa significa Seiryoku Zen'yō (精力善用)?", "Il miglior impiego dell'energia (massima efficienza)", ["Mutuo benessere e prosperità", "Cedevolezza e adattamento", "Perfezionamento di sé"], "Cap. 2, §2.2.")
h("02", "Che cosa significa Jita Kyōei (自他共栄)?", "Mutuo benessere e prosperità", ["Il miglior impiego dell'energia", "Sé e avversario in equilibrio", "Cedere per vincere"], "Cap. 2, §2.3: ji-ta = sé e gli altri; kyō-ei = fiorire insieme.")
h("02", "Qual è lo scopo ultimo del judo secondo Kanō (cap. 2)?", "Il perfezionamento di sé per contribuire al bene della società",
  ["La vittoria in gara", "La difesa personale efficace", "La conservazione delle tecniche del jūjutsu"], "Cap. 2, §2.4.")
h("02", "Qual è la catena logica corretta dei principi?", "Ju-no-ri (principio) → Seiryoku Zen'yō (metodo) → Jita Kyōei (scopo)",
  ["Jita Kyōei → Ju-no-ri → Seiryoku Zen'yō", "Seiryoku Zen'yō → Jita Kyōei → Ju-no-ri", "Ju-no-ri → Jita Kyōei → Seiryoku Zen'yō"], "Cap. 2, §2.4.")
h("02", "Con quale tecnica-principio il Seiryoku Zen'yō si incarna sul tatami?", "Il kuzushi (squilibrio)", ["Il kake", "Il rei", "L'atemi"], "Cap. 2, §2.2: proiettare dopo aver sbilanciato costa una frazione dell'energia.")
h("02", "Quale metafora usava Kanō per illustrare la cedevolezza?", "Il salice che cede alla neve, mentre il pino rigido si spezza", ["La quercia e il vento", "Il bambù e la spada", "L'acqua e la roccia"], "Cap. 2, §2.1 (immagine diffusa, di difficile riscontro negli scritti autografi).")
h("02", "Perché Kanō sostituì «jutsu» con «dō» nel nome «jūdō»?", "Per indicare una via di perfezionamento e non solo una tecnica",
  ["Per distinguere il judo dal kendō", "Per motivi di brevettazione della scuola", "Perché le percosse erano ammesse"], "Cap. 1, §1.2.")
h("02", "Che cosa indica il termine «rei» (礼) nel capitolo di filosofia?", "Il saluto e l'etichetta come forma educativa", ["La prosperità reciproca", "Lo squilibrio", "Il punto pieno"], "Cap. 2, §2.5.")
h("02", "Il «ju» del judo è…", "Un adattamento attivo e intelligente della propria forza", ["Una resa passiva", "Una difesa rigida", "Un tipo di presa"], "Cap. 2, §2.1: chi cede passivamente viene travolto.")

# 03 Fondamenti
h("03", "Che cos'è l'ai-yotsu (相四つ)?", "Guardia chiusa: entrambi impugnano dallo stesso lato", ["Guardia aperta: destro contro sinistro", "Presa alla cintura", "Presa a due mani sul bavero"], "Cap. 3, §3.1.")
h("03", "Che cos'è il kenka-yotsu (喧嘩四つ)?", "Guardia aperta: un combattente destro contro uno sinistro", ["Guardia chiusa dallo stesso lato", "Presa incrociata", "Doppio bavero"], "Cap. 3, §3.1: riguarda la guardia (quale mano funge da hikite), non la natura destra o mancina.")
h("03", "Come si muovono i piedi nel suri-ashi (摺足)?", "Strisciano sul tatami senza mai sollevarsi", ["Si sollevano a ogni passo", "Si incrociano", "Restano uniti"], "Cap. 3, §3.3.")
h("03", "Qual è la differenza tra ayumi-ashi e tsugi-ashi?", "Nell'ayumi-ashi un piede supera l'altro; nel tsugi-ashi i piedi non si superano mai",
  ["Nell'ayumi-ashi i piedi non si superano; nel tsugi-ashi sì", "L'ayumi-ashi è solo indietro, il tsugi-ashi solo avanti", "Sono la stessa cosa"], "Cap. 3, §3.3.")
h("03", "Su quale parte del piede avviene la rotazione nel tai-sabaki?", "Sull'avampiede (tsumasaki), mai sul tallone", ["Sul tallone", "Sul bordo esterno del piede", "Su entrambi i talloni"], "Cap. 3, §3.4.")
h("03", "Che cos'è il ma-ai (間合い)?", "La distanza-intervallo: distanza + timing + ritmo", ["Solo la distanza in centimetri", "Il saluto reciproco", "La presa al bavero"], "Cap. 3, §3.3.")
h("03", "Quale tra questi è un errore classico dello shintai?", "Incrociare i piedi durante lo spostamento", ["Strisciare i piedi", "Tenere il baricentro basso", "Guardare l'avversario"], "Cap. 3, §3.3: espone a de-ashi-harai e okuri-ashi-harai.")
h("03", "Che cos'è la tsurite (釣手)?", "La mano che impugna il bavero", ["La mano che impugna la manica", "Il piede di appoggio", "La rotazione posteriore"], "Cap. 3, §3.2 e cap. 12 (tsuri-te/hiki-te).")
h("03", "Che cos'è la presa standard (hon-kumi)?", "La presa con tsurite al bavero e hikite alla manica", ["La presa alla cintura", "La presa a due maniche", "La presa incrociata"], "Cap. 3, §3.2.")
h("03", "Che cosa è il «mae-mawari-sabaki»?", "Si avanza con un piede e si ruota davanti a uke volgendogli le spalle", ["Si arretra prendendo distanza", "Si avanza ad angolo retto senza ruotare", "Si tira uke avanti poi si ruota"], "Cap. 3, §3.4.")

# 04 Classificazione
h("04", "Quante tecniche di proiezione (Nage-waza) comprende l'elenco ufficiale Kōdōkan nel manuale?", "68", ["40", "32", "100"], "Cap. 4: Nage-waza 68; Katame-waza 32.")
h("04", "Quante tecniche di controllo (Katame-waza) comprende l'elenco ufficiale?", "32", ["68", "40", "21"], "Cap. 4.")
h("04", "In quale contesto compaiono le tecniche di Atemi-waza?", "Solo nei kata", ["Nel randori e in gara", "Solo in gara", "Nei programmi di cintura nera"], "Cap. 4, §1.")
h("04", "Quali sono i tre sottogruppi del Tachi-waza?", "Te-waza, Koshi-waza, Ashi-waza", ["Ma-sutemi, Yoko-sutemi, Makikomi", "Kesa, Shiho, Garami", "Ude, Ashi, Atama"], "Cap. 4 e cap. 16.")
h("04", "In che cosa si distinguono Ma-sutemi-waza e Yoko-sutemi-waza?", "Nel primo la caduta volontaria è di schiena, nel secondo di lato", ["Nel primo di lato, nel secondo di schiena", "Nel primo si usa la gamba, nel secondo il braccio", "Nel primo si cade su uke, nel secondo no"], "Cap. 4 e cap. 16.")
h("04", "Qual è il meccanismo efficace degli Shime-waza?", "La compressione delle arterie carotidi (e/o della trachea)", ["La iperestensione del gomito", "Il controllo del busto sul tatami", "La torsione della spalla"], "Cap. 4 e cap. 10.")
h("04", "Quanti sono i gruppi del Gokyō no waza?", "Cinque", ["Tre", "Quattro", "Otto"], "Cap. 4: Dai-ikkyō … Dai-gokyō (5° gruppo, la parte nuova del 4° dan).")

# 10 Katame-waza
h("10", "Quali sono le tre famiglie del Katame-waza?", "Osae-komi-waza, Shime-waza, Kansetsu-waza", ["Osae-komi, Nage, Atemi", "Shime, Garami, Hishigi", "Kesa, Shiho, Garami"], "Cap. 10, intro.")
h("10", "Che cosa significa «hairi-kata»?", "Il modo di entrare", ["Il modo di uscire", "Il controllo finale", "La forma modificata"], "Cap. 10 e cap. 12 (入り方).")
h("10", "Che cosa indica «kuzure»?", "La forma modificata di una tecnica", ["La forma base", "Il modo di entrare", "Un tipo di strangolamento"], "Cap. 10, §10.4: hon insegna il principio, kuzure dimostra di averlo compreso.")
h("10", "Come si distinguono le tre juji-jime?", "Kata-juji-jime, Nami-juji-jime, Gyaku-juji-jime", ["Hadaka, Okuri-eri, Kata-ha", "Nami, Gyaku, Sankaku", "Kata, Ryō-te, Tsukkomi"], "Cap. 10, §10.2: «juji» = croce (十).")
h("10", "Su quale articolazione agiscono le leve (kansetsu-waza) ammesse in gara?", "Solo sul gomito", ["Sul gomito e sulla spalla", "Sul polso e sul gomito", "Sul ginocchio"], "Cap. 10, §10.3.")
h("10", "Che cosa significa «Waki-gatame»?", "Leva ascellare", ["Leva con le braccia", "Leva addominale", "Leva triangolare"], "Cap. 10, §10.3 (腋固).")
h("10", "Che cosa significa «Okuri-eri-jime»?", "Strangolamento a bavero scorrevole", ["Strangolamento nudo", "Strangolamento ad ala singola", "Strangolamento a due mani"], "Cap. 10, §10.2 (送襟絞).")
h("10", "Che cosa significa «Hadaka-jime»?", "Strangolamento nudo", ["Strangolamento a bavero scorrevole", "Strangolamento triangolare", "Strangolamento ad affondo"], "Cap. 10, §10.2 (裸絞).")
h("10", "Quali tre elementi vanno controllati in un'immobilizzazione (Osae-komi)?", "Testa/spalle, busto, bacino", ["Mani, piedi, testa", "Collo, gomito, ginocchio", "Presa, distanza, ritmo"], "Cap. 10, §10.1: trascurarne uno apre la via di fuga.")
h("10", "Che cosa significa «Kesa-gatame»?", "Immobilizzazione a stola", ["Immobilizzazione dei quattro angoli", "Immobilizzazione di spalla", "Immobilizzazione a cuscino"], "Cap. 10 (袈裟固).")

# 11 Renraku, Gaeshi, Difese
h("11", "Qual è la differenza tra renzoku-waza e renraku-waza (in senso stretto)?", "Nel renzoku la seconda tecnica continua lo stesso movimento; nel renraku sfrutta la reazione di uke",
  ["Nel renzoku si sfrutta la reazione di uke; nel renraku no", "Il renzoku è al suolo, il renraku in piedi", "Sono sinonimi"], "Cap. 11, §11.1.")
h("11", "Uke irrigidisce e spinge indietro: quale tecnica favorisce?", "Una tecnica in avanti (es. Ippon-seoi-nage, Sumi-otoshi)", ["Una tecnica all'indietro (es. O-soto-gari)", "Una tecnica di gamba sull'appoggio", "Un sutemi di bacino"], "Cap. 11, §11.1.")
h("11", "Uke si china o arretra per difendersi: quale tecnica favorisce?", "Una tecnica all'indietro (es. O-soto-gari, O-uchi-gari)", ["Ippon-seoi-nage", "De-ashi-harai", "Yoko-guruma"], "Cap. 11, §11.1.")
h("11", "Contro quale attacco è tipico il Tsubame-gaeshi?", "De-ashi-harai", ["O-goshi", "Seoi-nage", "Harai-goshi"], "Cap. 11, §11.2: si ritira il piede e si spazza la gamba che avanza.")
h("11", "Quale di queste NON è una tecnica «gaeshi» in senso proprio?", "Ura-nage", ["O-soto-gaeshi", "Tsubame-gaeshi", "Uchi-mata-gaeshi"], "Cap. 11, §11.2: Ura-nage funziona da controtiro ma non ha nome in -gaeshi.")
h("11", "Quale ordine di preferenza delle difese indica il cap. 11?", "Prevenzione, schivata/spostamento, blocco, controtecnica", ["Blocco, controtecnica, prevenzione, schivata", "Controtecnica, blocco, schivata, prevenzione", "Schivata, blocco, prevenzione, controtecnica"], "Cap. 11, §11.3.")
h("11", "Quale catena di renraku è riportata nel cap. 11?", "De-ashi-harai → Uchi-mata", ["Uchi-mata → De-ashi-harai", "Seoi-nage → O-uchi-gari", "Tomoe-nage → Ko-uchi-gari"], "Cap. 11, §11.1.")
h("11", "Quale catena è attribuita a Mifune nel cap. 11?", "Ko-soto-gake → Sumi-otoshi", ["Ko-uchi-gari → Seoi-nage", "Harai-goshi → Tai-otoshi", "O-uchi-gari → Tai-otoshi"], "Cap. 11, §11.1.")
h("11", "Quali risposte tipiche si hanno contro Hane-goshi (cap. 11)?", "Ushiro-goshi, Ura-nage, Yoko-guruma, Hane-goshi-gaeshi", ["Uki-waza e Yoko-wakare", "O-uchi-gaeshi", "Tai-otoshi-gaeshi"], "Cap. 11, tabella dei kaeshi.")

# 13 Kime no Kata
h("13", "Come si ripartiscono le tecniche del Kime no Kata?", "8 Idori (in ginocchio) e 12 Tachiai (in piedi)", ["12 Idori e 8 Tachiai", "10 e 10", "6 Idori e 14 Tachiai"], "Cap. 13, intro.")
h("13", "In che anno Kanō presentò al Butokukai di Kyōto il kata a 20 tecniche?", "1906", ["1888", "1895", "1956"], "Cap. 13, Storia.")
h("13", "Quale kata di combattimento reale precedette il Kime no Kata (circa 1888)?", "Lo Shōbu no Kata (Shinken Shōbu no Kata)", ["Il Nage no Kata", "Il Goshin-jutsu", "Il Kime-shiki"], "Cap. 13, Storia.")
h("13", "Quale testo è oggi il riferimento ufficiale per esami e gare di kata?", "Il Kodokan Kata Textbook (2014)", ["Il Kōdōkan Shin Judo", "Il regolamento FIJLKAM 1977", "Il Textbook del 1956"], "Cap. 13, Storia.")
h("13", "Che cos'è il Kime-shiki, citato nel cap. 13?", "Una forma semplificata di 10 tecniche (5 Idori e 5 Tachiai), non valida all'esame", ["La forma attuale del Kōdōkan", "Il kata del 1948 di Londra", "La parte armata del kata"], "Cap. 13, Storia («Varianti non valide all'esame»).")
h("13", "Da quale posizione di partenza iniziano le tecniche Idori?", "Seiza (hizazume: due pugni tra le ginocchia)", ["Shizen-hontai a un passo", "Jigotai", "Ai-yotsu"], "Cap. 13, intro.")
h("13", "Quale punto vitale è l'Uto (烏兎)?", "Lo spazio tra le sopracciglia", ["Il plesso solare", "L'inguine", "La tempia"], "Cap. 13, tabella dei kyūsho.")
h("13", "Quale punto vitale è il Suigetsu (水月)?", "Il plesso solare", ["L'inguine", "Il mento", "La tempia"], "Cap. 13, tabella dei kyūsho.")
h("13", "Quale punto vitale è il Tsurigane (釣鐘)?", "L'inguine", ["Il plesso solare", "Il ginocchio", "Il mento"], "Cap. 13, tabella dei kyūsho.")
h("13", "Qual è la struttura in tre tempi di ogni tecnica del Kime no Kata?", "Schivata (tai-sabaki), colpo decisivo (atemi con kiai), controllo finale", ["Presa, kuzushi, kake", "Saluto, attacco, difesa", "Attacco, parata, proiezione"], "Cap. 13, intro.")
h("13", "Che cos'è lo zanshin (残心) nel Kime no Kata?", "La vigilanza residua di Tori dopo la tecnica, fino al mairi di Uke", ["Il saluto finale", "Il grido dell'attacco", "La distanza di partenza"], "Cap. 13, Principi.")
h("13", "Secondo i criteri IJF citati, un kiai assente è…", "Errore medio", ["Errore grave", "Errore piccolo", "Nessun errore"], "Cap. 13, Principi (un kiai superfluo è errore piccolo).")

# 14 Goshin-jutsu
h("14", "Qual è la data ufficiale di nascita del Kōdōkan Goshin-jutsu?", "1° gennaio 1956", ["1° gennaio 1906", "15 luglio 1987", "1° giugno 2006"], "Cap. 14, §1.1: riportata sul frontespizio del Textbook.")
h("14", "Quale ruolo ebbe Tomiki Kenji nella nascita del Goshin-jutsu?", "Fu la figura che portò l'influenza dell'aiki-jutsu, ed è documentata da Risei Kanō", ["Fu il presidente della commissione del 1941", "Fu il primo Uke ufficiale", "Non ebbe alcun ruolo"], "Cap. 14, §1.1–1.2.")
h("14", "A quale distanza iniziale si dispongono Tori e Uke nel Goshin-jutsu?", "Circa 5,5 m (tre ken)", ["Circa 2 m", "Circa 4 m", "Circa 8 m"], "Cap. 14, §2.1 e §3.1 (poi circa 4 m dopo ogni tecnica).")
h("14", "Come si dispongono Tori e Uke rispetto allo shōmen all'inizio?", "Tori a destra, Uke a sinistra", ["Tori a sinistra, Uke a destra", "Entrambi a destra", "Uno di fronte all'altro, al centro"], "Cap. 14, §2.1 e §3.1.")
h("14", "In quale ordine Uke depone le armi?", "Prima il bastone, poi il tantō, infine la pistola", ["Pistola, tantō, bastone", "Tantō, pistola, bastone", "Bastone, pistola, tantō"], "Cap. 14, §3.2.")
h("14", "In quale unico momento del Goshin-jutsu si usa la posizione seiza?", "Quando Uke deposita le armi", ["Nel saluto iniziale", "Durante le tecniche Toshu no bu", "Nel saluto finale"], "Cap. 14, §3.2.")
h("14", "Quale grafia è corretta per la tecnica n. 4 del Toshu no bu?", "Kataude-dori (片腕取)", ["Kata-ate-dori", "Katate-dori", "Kata-ude-tori"], "Cap. 14, §2.1 («errori di nomenclatura»).")
h("14", "Quale grafia ufficiale ha il n. 10 del Toshu no bu?", "Ganmen-tsuki (顔面突)", ["Gammen-tsuki", "Ganmen-zuki", "Kaomen-tsuki"], "Cap. 14, §2.1.")
h("14", "Quale formula sintetizza la filosofia del Goshin-jutsu?", "Fermare l'alabarda, concludere col minimo danno", ["Colpire per primi", "Ogni attacco è un'occasione", "Resistere fino alla resa"], "Cap. 14, §1.3.")
h("14", "In quali anni il frontespizio del Textbook registra le revisioni del Goshin-jutsu?", "1987, 1992 e 2004", ["1956, 1977 e 2006", "1906, 1948 e 1977", "1952, 1956 e 1987"], "Cap. 14, §1.4.")
h("14", "In quale anno il Kōdōkan costituì la commissione per la difesa personale (Goshinhō Seitei Iinkai)?", "1952 (settembre)", ["1941", "1956", "1948"], "Cap. 14, §1.1: nel 1941 era stata istituita la commissione sui rikakutaisei no waza.")

# 15 FIJLKAM
h("15", "Che natura giuridica ha la FIJLKAM?", "Federazione Sportiva Nazionale riconosciuta dal CONI", ["Ente pubblico", "Federazione internazionale", "Società per azioni"], "Cap. 15, §1.1.")
h("15", "Quali sono i tre Settori Federali previsti dallo Statuto?", "Judo, Lotta, Karate", ["Judo, Karate, Aikido", "Judo, Lotta, Pesistica", "Judo, Sumo, Karate"], "Cap. 15, §1.2 (art. 12 Statuto).")
h("15", "Qual è la federazione mondiale e quella europea del judo a cui la FIJLKAM è affiliata?", "IJF e EJU", ["WKF ed EKF", "UWW e UWW Europe", "IJF e UWW Europe"], "Cap. 15, §1.2.")
h("15", "In che anno e dove nacque l'antenata FAI (Federazione Atletica Italiana)?", "18 gennaio 1902, Milano", ["30 marzo 1924, Roma", "1933, Roma", "1 luglio 2000, Ostia"], "Cap. 15, §1.3.")
h("15", "Qual è la sequenza corretta delle denominazioni federali?", "FAI (1902) → FIAP (1933) → FILPJ (1974) → FILPJK (1995) → FIJLKAM (2000)",
  ["FAI → FILPJ → FIAP → FIJLKAM → FILPJK", "FIAP → FAI → FILPJ → FILPJK → FIJLKAM", "FAI → FIAP → FILPJK → FILPJ → FIJLKAM"], "Cap. 15, §1.3.")
h("15", "Da quando si chiama FIJLKAM la federazione?", "Dal 1° luglio 2000", ["Dal 1° gennaio 1995", "Dal 29 marzo 1981", "Dal 15 marzo 2013"], "Cap. 15, §1.3: i pesi confluiscono nella FIPE.")
h("15", "Dove ha sede la FIJLKAM?", "Ostia Lido (Roma), Centro Olimpico «Matteo Pellicone»", ["Milano", "Roma, Foro Italico", "Formia"], "Cap. 15, §1.3.")
h("15", "Quale organo è sovrano nella Federazione?", "L'Assemblea Nazionale", ["Il Consiglio Federale", "Il Presidente", "La Giunta CONI"], "Cap. 15, §2.1.")
h("15", "Come si esprime il voto delle società nell'Assemblea?", "In modo ponderato: un voto base più voti plurimi per la classifica del quadriennio", ["Un voto per società", "Un voto per tesserato", "Solo i presidenti regionali votano"], "Cap. 15, §2.1 (art. 6 Statuto).")
h("15", "Quanti tesserati attivi (stagione 2023) riporta il manuale?", "129.826", ["105.935", "83.516", "107.569"], "Cap. 15, §1.4: dati da verificare sulle fonti aggiornate.")
h("15", "Quando si riunisce l'Assemblea Nazionale Ordinaria elettiva?", "Entro il 15 marzo dell'anno successivo ai Giochi Olimpici", ["Ogni anno a gennaio", "Entro il 30 giugno di ogni anno", "Ogni due anni a ottobre"], "Cap. 15, §2.1.")
h("15", "Quante società minime servono per costituire un Comitato Regionale?", "Almeno 10 società con diritto di voto", ["Almeno 3", "Almeno 25", "Almeno 50"], "Cap. 15, §1.4: da verificare sullo Statuto in vigore.")

# 16 Suddivisione
h("16", "Quali sono le tre famiglie del judo Kōdōkan?", "Nage-waza, Katame-waza, Atemi-waza", ["Tachi-waza, Sutemi-waza, Makikomi-waza", "Te-waza, Koshi-waza, Ashi-waza", "Kesa, Shiho, Garami"], "Cap. 16 e cap. 4.")
h("16", "Quali gruppi compongono il Nage-waza?", "Tachi-waza, Sutemi-waza, Makikomi-waza", ["Te-waza, Koshi-waza, Ashi-waza", "Ma-sutemi, Yoko-sutemi, Atemi", "Osaekomi, Shime, Kansetsu"], "Cap. 16, §1.")
h("16", "Come si dividono gli Osaekomi-waza nel cap. 16?", "Kesa e Shiho", ["Garami e Hishigi", "Te-waza e Ashi-waza", "Respiratori e sanguigni"], "Cap. 16, §2.")
h("16", "Come si dividono i Kansetsu-waza nel cap. 16?", "Garami (torsioni) e Hishigi (iperestensioni)", ["Kesa e Shiho", "Ma e Yoko", "Respiratori e nervosi"], "Cap. 16, §2.")
h("16", "Come si classificano gli Shime-waza nel cap. 16?", "Respiratori, sanguigni, nervosi", ["Garami, Hishigi, Kesa", "Te, Koshi, Ashi", "Carotidi, giugulari, trachea"], "Cap. 16, §2.")
h("16", "Che cosa sono i Makikomi-waza?", "Tecniche in cui si avvolge l'avversario", ["Tecniche di caduta di schiena", "Tecniche di anca", "Tecniche di percossa"], "Cap. 16, §1.")

# 18 Difese Go / Chōwa / Yawara
h("18", "Che cosa significa il principio di difesa «Go» (剛)?", "Rompere, fermare: si oppone forza alla forza", ["Evitare, schivare", "Sostenere, cedere", "Annullare, rovescio"], "Cap. 18, §2.")
h("18", "Che cosa significa il principio di difesa «Chōwa» (調和)?", "Evitare, schivare con il tai-sabaki", ["Rompere, fermare", "Sostenere, cedere", "Contrattaccare di forza"], "Cap. 18, §2.")
h("18", "Che cosa significa il principio di difesa «Yawara» (柔)?", "Sostenere, cedere: usare l'energia di uke nella sua direzione prima che l'attacco sia efficace", ["Fermare con la forza", "Schivare alla fine dell'azione", "Bloccare con il peso"], "Cap. 18, §2.")
h("18", "Quale dei tre principi ha il costo energetico più alto?", "Go", ["Chōwa", "Yawara", "Nessuno: sono uguali"], "Cap. 18, §2.")
h("18", "Quale principio è il più difficile ma a costo più basso, secondo Sacripanti?", "Yawara", ["Go", "Chōwa", "Ura"], "Cap. 18, §2: richiede senso del tempo perfetto.")
h("18", "Quanti sono i principi di difesa secondo Sacripanti?", "Quattro: Go, Chōwa, Yawara e Ura", ["Tre: Go, Chōwa, Yawara", "Cinque", "Due: Go e Yawara"], "Cap. 18, §1: il programma ne cita tre; Ura è riportato per completezza.")
h("18", "Quali sono le tre classi di Chōwa in base alla direzione?", "Nami, gyaku, yoko", ["Mae, ushiro, yoko", "Go, nami, yawara", "Hon, kuzure, ura"], "Cap. 18, §2: stessa direzione, contraria, laterale.")
h("18", "Quale abbinamento di esempio riporta la fonte per il principio Go?", "Difesa Go contro uchi-mata", ["Difesa Go contro tai-otoshi", "Difesa Go contro morote-seoi-nage", "Difesa Go contro o-soto-gari"], "Cap. 18, §2.")
h("18", "Quale abbinamento di esempio riporta la fonte per il principio Chōwa?", "Difesa Chōwa contro tai-otoshi", ["Chōwa contro uchi-mata", "Chōwa contro morote-seoi-nage", "Chōwa contro o-soto-gari"], "Cap. 18, §2.")
h("18", "Quale abbinamento di esempio riporta la fonte per il principio Yawara?", "Difesa Yawara contro morote-seoi-nage", ["Yawara contro uchi-mata", "Yawara contro tai-otoshi", "Yawara contro o-soto-gari"], "Cap. 18, §2.")
h("18", "Quale dei principi NON è vicino al seiryoku zen'yō?", "Go", ["Chōwa", "Yawara", "Ura"], "Cap. 18, §2.")
h("18", "Che cosa descrive Ura (裏)?", "La ridirezione dell'energia dell'attaccante per eseguire una proiezione", ["Il blocco con il peso", "La schivata laterale", "La finta di attacco"], "Cap. 18, §2 (es. ura-nage, ushiro-goshi, utsuri-goshi).")

# 19 Sen / Go no sen / Sen no sen
h("19", "Che cosa indica «sen» (先) in Go no sen e Sen no sen?", "L'iniziativa (sente): il tempo in cui si prende il comando dello scontro", ["Il saluto", "La distanza", "La presa"], "Cap. 19, §1.")
h("19", "In quale momento si agisce nel Go no sen (後の先)?", "Dopo l'attacco avversario", ["Prima dell'attacco", "Durante la partenza dell'attacco", "Mai: è solo mentale"], "Cap. 19, §2.")
h("19", "In quale momento si agisce nel Sen no sen (先の先), secondo il cap. 19?", "Durante l'attacco, nel suo istante di partenza", ["Dopo l'attacco", "Prima che l'avversario pensi", "Dopo il kake"], "Cap. 19, §2.")
h("19", "In quale momento si agisce nel Sensen no sen (先々の先)?", "Prima dell'attacco, anticipando l'intenzione", ["Dopo l'attacco", "Durante il kake", "Alla fine dell'azione"], "Cap. 19, §2.")
h("19", "Nello schema di Sacripanti, a quale forma corrispondono i Kaeshi-waza?", "Sen no sen", ["Sen", "Go no sen", "Sensen no sen"], "Cap. 19, §3.")
h("19", "Nello schema di Sacripanti, a quale forma corrispondono i Bōgyo-waza (Go, Chōwa, Yawara, Ura)?", "Go no sen", ["Sen", "Sen no sen", "Sensen no sen"], "Cap. 19, §3.")
h("19", "Nello schema di Sacripanti, a quale forma corrispondono gli attacchi diretti, i renzoku/renraku e le finte?", "Sen", ["Go no sen", "Sen no sen", "Sensen no sen"], "Cap. 19, §3.")
h("19", "Sacripanti usa la forma «sensen no sen»?", "No, usa Sen, Go no sen e Sen no sen", ["Sì, come stadio più alto", "Sì, al posto di Sen", "Solo nel kendō"], "Cap. 19, §3.")
h("19", "Come si dimostrano all'esame, in sintesi, le tre forme dello schema di Sacripanti?", "Sen con i renraku, Go no sen con le difese, Sen no sen con i kaeshi", ["Sen con i kaeshi, Go no sen con i renraku, Sen no sen con le difese", "Tutte con i kata", "Tutte con il randori"], "Cap. 19, §3 «In sintesi per l'esame».")
h("19", "Il Go no sen è solo un semplice contrattacco?", "No: è anche uno stato mentale, un livello di concentrazione", ["Sì, è solo un contrattacco", "Sì, ma solo nel judo", "No: è solo una tecnica di gamba"], "Cap. 19, §4.")

for t, q, c, w, e in H:
    add(t, q, c, w, e)

# ---------------------------------------------------------------- uscita
topics = []
for f in sorted((ROOT / "content").glob("*.md")):
    tid = f.name[:2]
    title = re.sub(r"^#\s*", "", f.read_text(encoding="utf-8").splitlines()[0]).strip()
    n = sum(1 for q in Q if q["t"] == tid)
    if n:
        topics.append({"id": tid, "title": title, "n": n})

# controlli
for q in Q:
    assert len(q["o"]) == 4 and len(set(q["o"])) == 4, q
    assert q["t"] in {t["id"] for t in topics}, q
seen = set()
for q in Q:
    key = (q["t"], q["q"])
    assert key not in seen, key
    seen.add(key)

out = {"topics": topics, "q": Q}
(ROOT / "assets" / "quiz.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"OK: {len(Q)} domande in {len(topics)} argomenti")
for t in topics:
    print(f'  {t["id"]} {t["n"]:3d}  {t["title"][:60]}')
