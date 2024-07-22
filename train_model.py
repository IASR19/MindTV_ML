from builtins import Exception, input, print, str
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

def train_model(input_csvs, output_model='trained_model.pkl'):
    try:
        dataframes = [pd.read_csv(csv_file) for csv_file in input_csvs]
        df = pd.concat(dataframes)

        X = df[['IR', 'BPM', 'Avg_BPM', 'GSR']]
        y = df['Label']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        print(classification_report(y_test, predictions))

        joblib.dump(model, output_model)
        print(f"Modelo salvo em {output_model}")
    except Exception as e:
        print(f"Erro durante o treinamento do modelo: {str(e)}")

if __name__ == "__main__":
    input_csvs = input("Digite os arquivos CSV separados por vírgula: ").split(',')
    train_model(input_csvs)
