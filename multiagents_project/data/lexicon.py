# --------------------------------------------------------------------------
# 1. Parole che invertono il significato di un sintomo in un segmento
#    (usate per marcare RawSymptomMatch.negative = True)
# --------------------------------------------------------------------------
from domain_models.domain import SymptomEntry, AreaOfInterest, IntensityScale

NEGATIONS = [
    "non", "no", "niente", "nessun", "nessuna", "senza", "mai",
]

# --------------------------------------------------------------------------
# 2. Congiunzioni/punteggiatura su cui spezziamo la frase in segmenti.
#    Ogni segmento viene poi analizzato in isolamento (sintomo + area +
#    intensita' + negazione), cosi' una negazione o un'intensita' non
#    "sconfina" da un segmento all'altro.
# --------------------------------------------------------------------------
SEGMENT_SEPARATORS = [
    " e ", " ma ", " però ", " tuttavia ", ",", ";",
]

# --------------------------------------------------------------------------
# 3. Sintomi: concetto normalizzato -> lista di varianti testuali note.
#    Iniziamo con un piccolo set sufficiente a coprire i casi discussi
#    finora (dolore toracico, dispnea), da ampliare in seguito.
# --------------------------------------------------------------------------
SYMPTOM_ENTRIES = [
    SymptomEntry(
        concept="dolore",
        variants=["dolore", "male", "duole", "fa male"],
    ),
    SymptomEntry(
        concept="dispnea",
        variants=[
            "difficoltà a respirare", "difficoltà respiratoria",
            "fatica a respirare", "non riesco a respirare",
            "manca il respiro", "mi manca il respiro", "affanno",
        ],
    ),
    SymptomEntry(
        concept="febbre",
        variants=["febbre", "temperatura alta"],
    ),
    SymptomEntry(
        concept="nausea",
        variants=["nausea", "senso di vomito"],
    ),
]

# --------------------------------------------------------------------------
# 4. Aree del corpo: nome area normalizzato -> varianti testuali.
#    Usate per specializzare un sintomo generico (es. "dolore" + "torace"
#    -> concetto logico "dolore_torace") e per gestire l'eredità di
#    sintomo tra segmenti coordinati (es. "dolore al petto e alla schiena").
# --------------------------------------------------------------------------
AREA_OF_INTEREST = AreaOfInterest(
    areas={
        "torace": ["petto", "torace", "sterno"],
        "schiena": ["schiena", "dorso"],
        "testa": ["testa", "capo", "cranio", "fronte"],
        "addome": ["pancia", "addome", "stomaco", "ventre"],
        "arti_superiori": ["braccio", "braccia", "mano", "polso", "gomito"],
        "arti_inferiori": ["gamba", "gambe", "piede", "caviglia", "ginocchio"],
    }
)

# --------------------------------------------------------------------------
# 5. Scala di intensità: parola -> livello (1 = lieve, 4 = massimo).
#    Chiave = parola per permettere il lookup diretto durante la scansione
#    del testo (vedi ragionamento fatto insieme: Dict[str, int], non il
#    contrario).
# --------------------------------------------------------------------------
INTENSITY_SCALE = IntensityScale(
    scale={
        "lieve": 1, "leggero": 1, "leggera": 1,
        "moderato": 2, "moderata": 2,
        "forte": 3, "acuto": 3, "acuta": 3, "intenso": 3, "intensa": 3,
        "fortissimo": 4, "fortissima": 4, "insopportabile": 4,
        "lancinante": 4, "grave": 4,
    }
)