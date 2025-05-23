from graphviz import Digraph

# Création du diagramme UML simplifié
dot = Digraph('Architecture Technique du Système')

# Modules principaux
dot.node('A', 'app.py\nInterface utilisateur (Streamlit)')
dot.node('B', 'analyse.py\nCoordination des analyses')
dot.node('C', 'biomeca.py\nAngles articulaires, alignement')
dot.node('D', 'vitesses.py\nVitesses linéaires et angulaires')
dot.node('E', 'segmentation_evenementielle.py\nDécoupage des phases')
dot.node('F', 'extraction.py\nExtraction des données biomécaniques')
dot.node('G', 'visualisation.py\nVidéo, graphiques, image')
dot.node('H', 'rapport.py\nRapport PDF')
dot.node('I', 'notation_*.py\nNotation par type de geste')
dot.node('J', 'recommandations_*.py\nGénération de recommandations')
dot.node('K', 'detect_ball_yolo.py\nDétection du ballon')
dot.node('L', 'parametres_spatiaux.py\nAngle d’approche, pied d’appui')

# Relations
dot.edges([('A', 'B'), ('B', 'F'), ('B', 'C'), ('B', 'D'), ('B', 'E'),
           ('B', 'I'), ('B', 'J'), ('B', 'G'), ('B', 'H'), ('F', 'K'),
           ('B', 'L')])

# Affichage
dot.render('/mnt/data/uml_architecture_technique', format='png', cleanup=False)
'/mnt/data/uml_architecture_technique.png'
