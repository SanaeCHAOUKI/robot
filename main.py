import math
import time
import tkinter as tk

# =====================================================
# NOVA - visage minimal, 9 emotions
# Lancer :  python nova_visage.py
# =====================================================

BG = "#080C12"
PANEL = "#0D151D"
SCREEN = "#03080C"
TEXT = "#EAF4FF"
GREY = "#70858A"
RED = "#FF4055"
BLUE = "#4FC3F7"
OK = "#00F5A0"

W, H = 760, 400          # taille de l'ecran du robot
CX, CY = W // 2, 175     # centre du visage
SPACING = 125            # distance centre -> chaque oeil

# h = longueur, w = epaisseur, tilt = inclinaison (degres),
# dx / dy = decalage, color = couleur
EMOTIONS = {
    "VEILLE":    dict(h=84,  w=12, tilt=90,  dy=40,  dx=0,  color="#4F6F7C"),
    "ECOUTE":    dict(h=140, w=46, tilt=0,   dy=0,   dx=0,  color=TEXT),
    "REFLEXION": dict(h=120, w=42, tilt=0,   dy=-18, dx=24, color=BLUE),
    "PAROLE":    dict(h=140, w=46, tilt=0,   dy=0,   dx=0,  color=TEXT),
    "JOIE":      dict(h=140, w=46, tilt=0,   dy=0,   dx=0,  color=TEXT),
    "TRISTESSE": dict(h=115, w=44, tilt=-14, dy=20,  dx=0,  color="#7FB2FF"),
    "COLERE":    dict(h=100, w=46, tilt=22,  dy=8,   dx=0,  color=RED),
    "SURPRISE":  dict(h=185, w=52, tilt=0,   dy=-6,  dx=0,  color="#FFFFFF"),
    "ERREUR":    dict(h=140, w=46, tilt=0,   dy=0,   dx=0,  color=RED),
}

LABELS = {
    "VEILLE": "Veille", "ECOUTE": "Écoute", "REFLEXION": "Réflexion",
    "PAROLE": "Parole", "JOIE": "Joie", "TRISTESSE": "Tristesse",
    "COLERE": "Colère", "SURPRISE": "Surprise", "ERREUR": "Erreur",
}


# =====================================================
# Outils
# =====================================================

def mix(c1, c2, k):
    """Melange deux couleurs hex (k=0 -> c1, k=1 -> c2)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(
        round(x + (y - x) * k) for x, y in zip(a, b)
    )


def blink(now):
    """1.0 = oeil ouvert, descend vers 0.12 pendant un clignement."""
    p = ((now % 4.0) - 3.8) / 0.2
    if 0 < p < 1:
        return 1 - 0.88 * math.sin(p * math.pi)
    return 1.0


# =====================================================
# Le visage
# =====================================================

class Face:
    def __init__(self, canvas):
        self.c = canvas
        self.state = "VEILLE"
        self.t0 = time.monotonic()
        self.cur = dict(EMOTIONS["VEILLE"])   # valeurs affichees (lissees)

    def set_state(self, state):
        self.state = state
        self.t0 = time.monotonic()

    # --- formes de base ---------------------------------
    def line(self, pts, width, color):
        flat = [v for p in pts for v in p]
        self.c.create_line(
            *flat, width=width, fill=color,
            capstyle="round", joinstyle="round", tags="anim"
        )

    def bar(self, x, y, length, thick, tilt, color):
        """Barre arrondie : un trait epais aux bouts ronds."""
        half = max(0.5, (length - thick) / 2)
        a = math.radians(tilt)
        dx, dy = half * math.sin(a), half * math.cos(a)
        self.line([(x + dx, y - dy), (x - dx, y + dy)], thick, color)

    # --- dessin d'une image -----------------------------
    def draw(self):
        now = time.monotonic()
        t = now - self.t0
        s = self.state
        tgt = EMOTIONS[s]
        cur = self.cur

        # transition douce vers l'emotion cible
        for key in ("h", "w", "tilt", "dy", "dx"):
            cur[key] += (tgt[key] - cur[key]) * 0.18
        cur["color"] = mix(cur["color"], tgt["color"], 0.18)

        self.c.delete("anim")

        # effets propres a chaque emotion
        k, wk = 1.0, 1.0
        if s not in ("VEILLE", "SURPRISE"):
            k *= blink(now)
        if s == "ECOUTE":
            p = 1 + 0.03 * math.sin(t * 4)
            k *= p
            wk = p
        if s == "SURPRISE":
            p = 1 + 0.15 * math.exp(-t * 4) * math.cos(t * 14)
            k *= p
            wk = p

        w = cur["w"] * wk
        h = max(w, cur["h"] * k)
        dx, dy = cur["dx"], cur["dy"]

        if s in ("ECOUTE", "PAROLE"):
            dx += math.sin(now * 0.7) * 8
        if s == "REFLEXION":
            dx += math.sin(t * 2) * 6
        if s == "VEILLE":
            dy += math.sin(now * 1.5) * 4
        if s == "JOIE":
            dy += math.sin(t * 6) * 3
        if s == "COLERE":
            dx += math.sin(t * 40) * 1.5

        # les deux yeux
        for side in (-1, 1):
            x = CX + side * SPACING + dx
            y = CY + dy

            if s == "JOIE":
                pts = []
                for d in range(30, 151, 5):
                    r = math.radians(d)
                    pts.append((x + 48 * math.cos(r), y + 34 - 48 * math.sin(r)))
                self.line(pts, 24, cur["color"])
            elif s == "ERREUR":
                self.line([(x - 42, y - 42), (x + 42, y + 42)], 22, cur["color"])
                self.line([(x + 42, y - 42), (x - 42, y + 42)], 22, cur["color"])
            else:
                self.bar(x, y, h, w, cur["tilt"] * side, cur["color"])

        # decors
        if s == "REFLEXION":
            for i in range(3):
                px = CX - 40 + i * 40
                py = 50 + 8 * math.sin(t * 3 + i)
                self.c.create_oval(
                    px - 6, py - 6, px + 6, py + 6,
                    fill=BLUE, outline="", tags="anim"
                )

        if s in ("ECOUTE", "PAROLE"):
            amp = 24 if s == "PAROLE" else 5
            col = TEXT if s == "PAROLE" else "#2C4A57"
            for i in range(7):
                bx = CX + (i - 3) * 22
                bh = 4 + amp * abs(math.sin(now * 8 + i * 0.9))
                self.line([(bx, 335 - bh), (bx, 335 + bh)], 8, col)

        if s == "ERREUR" and int(t * 4) % 2 == 0:
            self.c.create_rectangle(
                6, 6, W - 6, H - 6, outline=RED, width=3, tags="anim"
            )


# =====================================================
# Fenetre
# =====================================================

root = tk.Tk()
root.title("NOVA")
root.geometry("820x800")
root.configure(bg=BG)
root.resizable(False, False)

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=30, pady=(18, 6))

tk.Label(header, text="NOVA", font=("Arial", 24, "bold"),
         bg=BG, fg=TEXT).pack(side="left")

status = tk.Label(header, text="● Veille", font=("Arial", 10, "bold"),
                  bg=BG, fg=GREY)
status.pack(side="right")

canvas = tk.Canvas(root, width=W, height=H, bg=SCREEN,
                   highlightthickness=1, highlightbackground="#1B2A33")
canvas.pack(pady=8)

face = Face(canvas)
job = None   # tache planifiee en cours


def show_state(state):
    face.set_state(state)
    color = RED if state in ("COLERE", "ERREUR") else OK
    if state == "VEILLE":
        color = GREY
    status.config(text="● " + LABELS[state], fg=color)


def play(sequence):
    """Joue une suite [(etat, duree_ms), ...] ; le dernier reste affiche."""
    global job
    if job is not None:
        root.after_cancel(job)
        job = None
    if not sequence:
        return
    (state, duration), rest = sequence[0], sequence[1:]
    show_state(state)
    if rest:
        job = root.after(duration, lambda: play(rest))


# --- boutons de test --------------------------------------------------
buttons = tk.Frame(root, bg=BG)
buttons.pack(pady=4)

for key in EMOTIONS:
    tk.Button(
        buttons, text=LABELS[key], width=8,
        bg=PANEL, fg=TEXT, activebackground="#16222C",
        activeforeground=TEXT, relief="flat", font=("Arial", 9),
        command=lambda k=key: play([(k, 0)])
    ).pack(side="left", padx=2)

# --- conversation -----------------------------------------------------
chat = tk.Text(root, height=6, bg=PANEL, fg=TEXT, font=("Arial", 10),
               wrap="word", relief="flat", padx=12, pady=8, state="disabled")
chat.pack(fill="x", padx=30, pady=(12, 6))


def add_message(sender, message):
    chat.config(state="normal")
    chat.insert(tk.END, sender + "  >  " + message + "\n")
    chat.see(tk.END)
    chat.config(state="disabled")


KEYWORDS = {
    "JOIE": ["content", "heureux", "super", "merci", "génial", "genial",
             "bravo", "cool", "happy"],
    "TRISTESSE": ["triste", "malheureux", "déprimé", "deprime", "seul", "sad"],
    "COLERE": ["colère", "colere", "énervé", "enerve", "furieux", "angry"],
    "SURPRISE": ["wow", "incroyable", "surpris", "surprise"],
    "ERREUR": ["erreur", "bug", "panne", "problème", "probleme", "error"],
}

REPLIES = {
    "JOIE": "Ça me fait plaisir ! Continuez comme ça.",
    "TRISTESSE": "Je suis désolé. Je reste là si vous voulez parler.",
    "COLERE": "Respirez un instant. On va régler ça ensemble.",
    "SURPRISE": "Vraiment ? Racontez-moi tout.",
    "ERREUR": "Un problème est survenu. Essayons à nouveau.",
    "ECOUTE": "Je vous écoute. Dites-m'en plus.",
}


def detect_emotion(message):
    message = message.lower()
    for emotion, words in KEYWORDS.items():
        if any(w in message for w in words):
            return emotion
    return "ECOUTE"


def send_message(event=None):
    message = entry.get().strip()
    if not message:
        return
    entry.delete(0, tk.END)
    add_message("VOUS", message)

    emotion = detect_emotion(message)
    add_message("NOVA", REPLIES[emotion])

    play([
        ("REFLEXION", 1200),
        ("PAROLE", 2400),
        (emotion, 2500),
        ("ECOUTE", 15000),
        ("VEILLE", 0),
    ])


input_frame = tk.Frame(root, bg=BG)
input_frame.pack(fill="x", padx=30, pady=8)

entry = tk.Entry(input_frame, bg="#121E28", fg=TEXT, insertbackground=TEXT,
                 font=("Arial", 12), relief="flat")
entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))
entry.bind("<Return>", send_message)

tk.Button(input_frame, text="Envoyer", command=send_message,
          bg=TEXT, fg="#06120D", relief="flat", font=("Arial", 10, "bold"),
          padx=18, pady=6).pack(side="right")


# =====================================================
# Boucle d'animation
# =====================================================

def animate():
    face.draw()
    root.after(30, animate)


add_message("NOVA", "Système initialisé. Je suis prêt.")
play([("VEILLE", 1500), ("ECOUTE", 15000), ("VEILLE", 0)])
animate()
root.mainloop()