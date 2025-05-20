from fpdf import FPDF
import os

class RapportPDF(FPDF):
    def __init__(self, type_geste="Instep"):
        super().__init__()
        self.type_geste = type_geste
        font_dir = "ttf"
        self.add_font("DejaVu", "", os.path.join(font_dir, "DejaVuSans.ttf"), uni=True)
        self.add_font("DejaVu", "B", os.path.join(font_dir, "DejaVuSans-Bold.ttf"), uni=True)
        self.set_font("DejaVu", "", 11)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("DejaVu", "B", 16)
        self.set_text_color(0, 0, 0)
        titre = f"Rapport biomécanique du tir – Analyse {self.type_geste}"
        self.cell(0, 10, titre, ln=True, align="C")
        self.ln(5)

    def section_title(self, title, r=0, g=0, b=128):
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(r, g, b)
        self.set_x(10)
        self.cell(0, 8, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.set_font("DejaVu", "", 11)

    def safe_multicell(self, text):
        self.set_x(10)
        self.multi_cell(190, 6, str(text))


def generer_rapport_pdf(notes_par_phase, score_global, details_score,
                        points_forts, points_a_ameliorer,
                        recommandations, reco_globale,
                        image_path="impact_pose.png",
                        graphe1="graphes/vitesses_kickstep_impact.png",
                        graphe2="graphes/vitesse_pied_phases.png",
                        nom_fichier="rapport_analyse.pdf",
                        nom_joueuse="",
                        type_geste="Instep"):  # <- ajout ici

    pdf = RapportPDF(type_geste=type_geste)  # <- passage ici
    pdf.add_page()

    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(0, 10, f"Joueuse : {nom_joueuse}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)

    if os.path.exists(image_path):
        pdf.ln(5)
        pdf.image(image_path, w=100)
    else:
        pdf.safe_multicell("Image de pose à l’impact non disponible.")
    pdf.ln(8)

    # 1. Notes
    pdf.section_title("1. Notes par phase", 0, 102, 204)
    for phase, note in notes_par_phase.items():
        pdf.safe_multicell(f"- {phase.capitalize()} : {note}/10")
    pdf.ln(4)

    # 2. Score global
    pdf.section_title("2. Score global", 0, 102, 204)
    pdf.safe_multicell(f"Score final : {round(score_global, 2)}/10")
    pdf.ln(4)

    # 3. Points forts
    pdf.section_title("3. Points forts", 0, 153, 0)
    if points_forts:
        for pf in points_forts:
            pdf.safe_multicell(f"• {pf}")
    else:
        pdf.safe_multicell("Aucun point fort détecté.")
    pdf.ln(4)

    # 4. À améliorer
    pdf.section_title("4. Points à améliorer", 204, 0, 0)
    if points_a_ameliorer:
        for pa in points_a_ameliorer:
            pdf.safe_multicell(f"• {pa}")
    else:
        pdf.safe_multicell("Aucune faiblesse majeure détectée.")
    pdf.ln(4)

    # 5. Recommandations
    pdf.section_title("5. Recommandations spécifiques", 153, 51, 255)
    for phase, erreur, reco in recommandations:
        texte = f"[{phase}] {erreur} → {reco}"
        pdf.safe_multicell(texte)
    pdf.ln(4)

    # 6. Synthèse
    pdf.section_title("6. Synthèse globale", 255, 102, 0)
    pdf.safe_multicell(reco_globale)

    # 7. Graphiques
    if os.path.exists(graphe1):
        pdf.add_page()
        pdf.section_title("7. Graphique – Vitesses pendant le Kick Step et l’impact")
        pdf.image(graphe1, w=180)

    if os.path.exists(graphe2):
        pdf.add_page()
        pdf.section_title("8. Graphique – Évolution globale de la vitesse du pied")
        pdf.image(graphe2, w=180)

    pdf.output(nom_fichier)
    return nom_fichier
