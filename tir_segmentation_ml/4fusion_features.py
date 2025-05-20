import pandas as pd
import pandas as pd
import os

# Chemin du dossier contenant les fichiers CSV
folder_path = 'tir_segmentation_ml/data/Features_annotated'

# Lister et trier tous les fichiers CSV sauf celui des 3 phases
csv_files = sorted(
    [f for f in os.listdir(folder_path) if f.endswith('.csv') and '3phases' not in f],
    key=lambda x: int(''.join(filter(str.isdigit, x)))
)

# Fusionner les fichiers
dfs = []
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    df['source_file'] = file  # Optionnel : garde la trace de l’origine
    dfs.append(df)

# Concaténer tous les DataFrames
df_merged = pd.concat(dfs, ignore_index=True)

# Sauvegarder dans un fichier unique
output_path = 'tir_segmentation_ml/data/features_annotated_global.csv'
df_merged.to_csv(output_path, index=False)

print(f"✅ Fusion terminée. Fichier généré : {output_path}")

# Charger ton fichier CSV annoté
df = pd.read_csv("tir_segmentation_ml/data/Features_annotated_global.csv")

# Compter le nombre d'occurrences de chaque phase
compte = df["label"].value_counts()

# Affichage
print("📊 Répartition des fenêtres annotées par phase :")
print(compte)
