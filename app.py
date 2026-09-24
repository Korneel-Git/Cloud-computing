"""
Storingsmelder - een klein meldingensysteem voor storingen.

Cloud computing (B-UCLL-MGN13A), Graduaat Systeem- en netwerkbeheer, UCLL.

Deze applicatie draait in twee standen:

  Geen DATABASE_URL ingesteld  ->  slaat op in een SQLite-bestand
  Wel DATABASE_URL ingesteld   ->  slaat op in PostgreSQL

Dat is geen truc voor de les. Configuratie die uit een environment variable komt
en een verstandige standaardwaarde heeft, is hoe applicaties gebouwd worden die
in meerdere omgevingen moeten draaien.
"""

import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# ------------------------------------------------------------------ instellingen

DATABASE_URL = os.environ.get("DATABASE_URL", "")
SQLITE_PAD = os.environ.get("SQLITE_PAD", "/data/storingen.db")
APP_TITEL = os.environ.get("APP_TITEL", "Storingsmelder")

# Postgres en SQLite schrijven hun parameters anders. We zetten het teken hier
# een keer vast in plaats van het overal in de query's te herhalen.
PARAM = "%s" if DATABASE_URL else "?"

PRIORITEITEN = ["laag", "normaal", "hoog"]


# -------------------------------------------------------------------- database

def verbinding():
    """Geeft een verbinding met de database die op dit moment ingesteld is."""
    if DATABASE_URL:
        import psycopg
        return psycopg.connect(DATABASE_URL)

    import sqlite3
    map_van_bestand = os.path.dirname(SQLITE_PAD)
    if map_van_bestand:
        os.makedirs(map_van_bestand, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PAD)
    return conn


def maak_tabel():
    """Maakt de tabel aan als ze nog niet bestaat."""
    if DATABASE_URL:
        ddl = """
            CREATE TABLE IF NOT EXISTS meldingen (
                id            SERIAL PRIMARY KEY,
                titel         TEXT NOT NULL,
                locatie       TEXT NOT NULL,
                omschrijving  TEXT NOT NULL DEFAULT '',
                prioriteit    TEXT NOT NULL DEFAULT 'normaal',
                status        TEXT NOT NULL DEFAULT 'open',
                gemeld_op     TEXT NOT NULL
            )
        """
    else:
        ddl = """
            CREATE TABLE IF NOT EXISTS meldingen (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                titel         TEXT NOT NULL,
                locatie       TEXT NOT NULL,
                omschrijving  TEXT NOT NULL DEFAULT '',
                prioriteit    TEXT NOT NULL DEFAULT 'normaal',
                status        TEXT NOT NULL DEFAULT 'open',
                gemeld_op     TEXT NOT NULL
            )
        """
    with verbinding() as conn:
        cur = conn.cursor()
        cur.execute(ddl)
        conn.commit()


def alle_meldingen():
    with verbinding() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, titel, locatie, omschrijving, prioriteit, status, gemeld_op"
            " FROM meldingen ORDER BY status DESC, id DESC"
        )
        rijen = cur.fetchall()

    kolommen = ["id", "titel", "locatie", "omschrijving", "prioriteit", "status", "gemeld_op"]
    return [dict(zip(kolommen, rij)) for rij in rijen]


def melding_toevoegen(titel, locatie, omschrijving, prioriteit):
    with verbinding() as conn:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO meldingen (titel, locatie, omschrijving, prioriteit, status, gemeld_op)"
            f" VALUES ({PARAM}, {PARAM}, {PARAM}, {PARAM}, 'open', {PARAM})",
            (titel, locatie, omschrijving, prioriteit,
             datetime.now().strftime("%d/%m/%Y %H:%M")),
        )
        conn.commit()


def melding_sluiten(melding_id):
    with verbinding() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE meldingen SET status = 'gesloten' WHERE id = {PARAM}",
            (melding_id,),
        )
        conn.commit()


# ----------------------------------------------------------------------- routes

@app.route("/")
def overzicht():
    meldingen = alle_meldingen()
    return render_template(
        "overzicht.html",
        titel=APP_TITEL,
        meldingen=meldingen,
        prioriteiten=PRIORITEITEN,
        open_aantal=sum(1 for m in meldingen if m["status"] == "open"),
        opslag="PostgreSQL" if DATABASE_URL else "SQLite",
    )


@app.route("/melden", methods=["POST"])
def melden():
    titel = request.form.get("titel", "").strip()
    locatie = request.form.get("locatie", "").strip()
    omschrijving = request.form.get("omschrijving", "").strip()
    prioriteit = request.form.get("prioriteit", "normaal")

    if prioriteit not in PRIORITEITEN:
        prioriteit = "normaal"

    if titel and locatie:
        melding_toevoegen(titel, locatie, omschrijving, prioriteit)

    return redirect(url_for("overzicht"))


@app.route("/sluiten/<int:melding_id>", methods=["POST"])
def sluiten(melding_id):
    melding_sluiten(melding_id)
    return redirect(url_for("overzicht"))


@app.route("/health")
def health():
    """Zegt of de applicatie draait en of ze haar database kan bereiken."""
    try:
        with verbinding() as conn:
            conn.cursor().execute("SELECT 1")
        return {"status": "ok", "opslag": "PostgreSQL" if DATABASE_URL else "SQLite"}, 200
    except Exception as fout:
        return {"status": "fout", "melding": str(fout)}, 503


# ------------------------------------------------------------------- opstarten

maak_tabel()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
