import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import ADASYN
import pickle
import os

# === PARAMÈTRES ===
DATA_PATH = "tir_segmentation_ml/data/features_annotated_global.csv"           # Fichier des données annotées
MODEL_OUTPUT_PATH = "tir_segmentation_ml/data/modele_segmentateur_adasyn.pkl"  # Chemin de sauvegarde du modèle
TEST_SIZE = 0.2                                                                 # Pourcentage de données pour le test
RANDOM_STATE = 42                                                               # Graine aléatoire pour reproductibilité

# === 1. Vérification de l'existence du fichier
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Fichier non trouvé : {DATA_PATH}")

# === 2. Chargement et nettoyage des données
df = pd.read_csv(DATA_PATH)
if "frame_centrale" in df.columns:
    df = df.drop(columns=["frame_centrale"])  # Suppression éventuelle d'une colonne inutile

df = df[df["label"] != "unknown"]             # Suppression des lignes sans annotation
df = df.dropna()                              # Suppression des lignes avec valeurs manquantes

# Suppression des exemples où les colonnes de mouvement sont quasi constantes
# Ne garder que les colonnes numériques pour vérifier la variabilité
angle_cols = [col for col in df.columns if col != "label" and pd.api.types.is_numeric_dtype(df[col])]

# Supprimer les lignes où la std des colonnes numériques est trop faible (ex: mouvement constant)
df = df[df[angle_cols].std(axis=1) > 1e-2]

# === 3. Encodage des labels (catégories → entiers)
df["label"] = df["label"].astype("category")
y = df["label"].cat.codes                     # Codes numériques des labels
label_names = df["label"].cat.categories     # Noms originaux des classes
X = df.drop(columns=["label"])

# ✅ Correction ici : garder uniquement les colonnes numériques
X = X.select_dtypes(include=["number"])


# === 4. Rééquilibrage des classes avec ADASYN
adasyn = ADASYN(random_state=RANDOM_STATE)
X_resampled, y_resampled = adasyn.fit_resample(X, y)

# === 5. Séparation des données en entraînement et test
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_resampled
)

# === 6. Entraînement du modèle Random Forest
clf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=RANDOM_STATE)
clf.fit(X_train, y_train)

# === 7. Évaluation du modèle
y_pred = clf.predict(X_test)

print("=== Rapport de classification (ADASYN) ===")
print(classification_report(y_test, y_pred, target_names=label_names))

print("=== Matrice de confusion ===")
print(confusion_matrix(y_test, y_pred))

# === 8. Sauvegarde du modèle entraîné
with open(MODEL_OUTPUT_PATH, "wb") as f:
    pickle.dump(clf, f)

print(f"Modèle équilibré sauvegardé dans : {MODEL_OUTPUT_PATH}")
