import pandas as pd
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from sklearn.tree import plot_tree

from src.logic.data import cargar_estaciones_api

API_URL = (
    "https://gis.transmilenio.gov.co/arcgis/rest/services/"
    "Troncal/consulta_estaciones_troncales/FeatureServer/0/"
    "query?outFields=*&where=1%3D1&f=geojson"
)

# 1. Obtener datos desde la API
estaciones = cargar_estaciones_api(API_URL)

# 2. Crear DataFrame
df = pd.DataFrame(estaciones)
df = df[(df['latitud'] != 0) & (df['lon'] != 0)]

# 3. Codificar etiquetas de troncal
le = LabelEncoder()
df['troncal_id'] = le.fit_transform(df['troncal'])

# 4. Entrenamiento del modelo
X = df[['latitud', 'lon']]
y = df['troncal_id']
modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
modelo.fit(X, y)

# 5. Guardado del modelo y el codificador
joblib.dump(modelo, "resources/modelo_troncal.pkl")
joblib.dump(le, "resources/label_encoder_troncal.pkl")

print("\u2705 Modelo entrenado correctamente con datos de la API.")

# Cargar modelo y encoder para predicción posterior
modelo = joblib.load("resources/modelo_troncal.pkl")
encoder = joblib.load("resources/label_encoder_troncal.pkl")

def predecir_troncal_por_coords(lat, lon):
    df_input = pd.DataFrame([[lat, lon]], columns=['latitud', 'lon'])
    pred_code = modelo.predict(df_input)[0]
    troncal = encoder.inverse_transform([pred_code])[0]

    print(type(modelo)) # Verificar el tipo de modelo
    # Cargar el codificador para ver las etiquetas originales
    print(encoder.classes_)  # Ver las etiquetas originales (troncales)

    estimator = modelo.estimators_[0]  # Obtener el primer árbol del bosque

    # Visualizar el árbol y guardarlo como imagen
    plt.figure(figsize=(20, 10))
    plot_tree(estimator, feature_names=["latitud", "lon"], filled=True)
    plt.savefig("resources/arbol_decision.png")  # Guardar el árbol como imagen
    plt.close()
    print("Árbol de decisión guardado como 'resources/arbol_decision.png'.")
    return troncal


