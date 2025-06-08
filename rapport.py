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
        self.logo_path = "img_WAC.png"

    def bold_text(self, text, r=220, g=20, b=60):
        self.set_font("DejaVu", "B", 11)
        self.set_text_color(r, g, b)
        self.write(6, text)
        self.set_font("DejaVu", "", 11)
        self.set_text_color(0, 0, 0)

    def header(self):
        logo_w = 18
        y_logo = 7
        if os.path.exists(self.logo_path):
            # Gauche
            self.image(self.logo_path, x=8, y=y_logo, w=logo_w)
            # Droite (w=210mm pour A4, marge ~10mm)
            self.image(self.logo_path, x=self.w - logo_w - 8, y=y_logo, w=logo_w)
        self.set_font("DejaVu", "B", 16)
        self.set_text_color(220, 20, 60)
        titre = f"Rapport biomécanique du tir – Analyse {self.type_geste}"
        self.cell(0, 18, titre, ln=True, align="C")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def section_title(self, title, r=0, g=0, b=128):
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(r, g, b)
        self.set_x(10)
        self.cell(0, 8, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.set_font("DejaVu", "", 11)

    def centered_title(self, title, size=11):
        self.set_font("DejaVu", "B", size)
        self.cell(0, 10, title, ln=True, align="C")
        self.set_font("DejaVu", "", 11)
        self.ln(2)

    def safe_multicell(self, text):
        self.set_x(10)
        self.multi_cell(190, 6, str(text))


def generer_rapport_pdf(notes_par_phase, score_global, details_score,
                        points_forts, points_a_ameliorer,
                        recommandations, reco_globale,
                        image_path="impact_pose.png",
                        graphe1="graphes/graphe_vitesse_lineaire.png",
                        graphe2="graphes/graphe_vitesse_angulaire.png",
                        radar_path="graphes/radar_notes.png",
                        nom_fichier="rapport_analyse.pdf",
                        nom_joueuse="",
                        type_geste="Instep"):

    pdf = RapportPDF(type_geste=type_geste)
    pdf.add_page()

    # ✅ Affichage du Nom de la joueuse
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(0, 10, f"Joueuse : {nom_joueuse}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)

    # ✅ Image de la pose à l’impact réduite
    if os.path.exists(image_path):
        pdf.ln(5)
        image_width = 60
        x_position = (pdf.w - image_width) / 2
        pdf.image(image_path, x=x_position, w=image_width)
        pdf.ln(8)
    else:
        pdf.safe_multicell("Image de pose à l’impact non disponible.")
    pdf.ln(8)

    # 1. Notes par phase
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
            # Si c'est une dict, on prend la clé 'titre' ou str
            if isinstance(pf, dict):
                titre = pf.get("titre", "")
                explication = pf.get("explication", "")
                pdf.set_font("DejaVu", "B", 11)
                pdf.safe_multicell(f"• {titre}")
                pdf.set_font("DejaVu", "", 11)
                pdf.safe_multicell(f"{explication}")
            else:
                pdf.safe_multicell(f"• {str(pf)}")
            pdf.ln(2)
    else:
        pdf.safe_multicell("Aucun point fort détecté.")
    pdf.ln(4)

    # 4. Points à améliorer
    pdf.section_title("4. Points à améliorer", 204, 0, 0)
    if points_a_ameliorer:
        for pa in points_a_ameliorer:
            if isinstance(pa, dict):
                titre = pa.get("titre", "")
                explication = pa.get("explication", "")
                pdf.set_font("DejaVu", "B", 11)
                pdf.safe_multicell(f"• {titre}")
                pdf.set_font("DejaVu", "", 11)
                pdf.safe_multicell(f"{explication}")
            else:
                pdf.safe_multicell(f"• {str(pa)}")
            pdf.ln(2)
    else:
        pdf.safe_multicell("Aucune faiblesse majeure détectée.")
    pdf.ln(4)

        # 5. Recommandations spécifiques
    pdf.section_title("5. Recommandations spécifiques", 153, 51, 255)
    for phase, erreur, reco in recommandations:
        # Découpage Objectif et Exercice
        lignes = reco.split('\n')
        objectif, exercice = "", ""
        for l in lignes:
            if "Objectif" in l: objectif = l.strip()
            if "Exercice" in l: exercice = l.strip()
        # Phase en gras et rouge (ou violet si tu préfères)
        pdf.set_font("DejaVu", "B", 11)
        pdf.set_text_color(220, 20, 60)   # Rouge vif
        pdf.safe_multicell(f"[{phase.capitalize()}]")
        pdf.set_text_color(0, 0, 0)
        # Erreur
        pdf.set_font("DejaVu", "", 11)
        pdf.safe_multicell(erreur)
        # Objectif
        if objectif:
            pdf.set_font("DejaVu", "B", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.write(6, "Objectif : ")
            pdf.set_font("DejaVu", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, objectif.replace("Objectif :", "").strip())
        # Exercice
        if exercice:
            pdf.set_font("DejaVu", "B", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.write(6, "Exercice : ")
            pdf.set_font("DejaVu", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, exercice.replace("Exercice :", "").strip())
        pdf.ln(2)
    pdf.ln(2)


    # 6. Synthèse globale
    pdf.section_title("6. Synthèse globale", 255, 102, 0)
    pdf.safe_multicell(reco_globale)

    # 7. Visualisations – Radar + Graphiques
    pdf.add_page()
    pdf.section_title("7. Visualisation biomécanique : Radar et vitesses", 0, 102, 204)

    if os.path.exists(radar_path):
        pdf.centered_title("Radar des scores par phase", size=12)
        radar_width = 80
        x_position = (pdf.w - radar_width) / 2
        pdf.image(radar_path, x=x_position, w=radar_width)
        pdf.ln(6)

    if os.path.exists(graphe1):
        pdf.centered_title("Évolution des vitesses segmentaires (Kick Step + Impact)", size=12)
        image_width = 160
        x_position = (pdf.w - image_width) / 2
        pdf.image(graphe1, x=x_position, w=image_width)
        pdf.ln(6)

    if os.path.exists(graphe2):
        pdf.centered_title("Évolution de la vitesse du pied de frappe", size=12)
        image_width = 160
        x_position = (pdf.w - image_width) / 2
        pdf.image(graphe2, x=x_position, w=image_width)
    else:
        pdf.safe_multicell("Graphiques de vitesses non disponibles.")

    pdf.output(nom_fichier)
    return nom_fichier
