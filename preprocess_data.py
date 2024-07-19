import pandas as pd

def preprocess_data(input_csv='sensor_data.csv', output_csv='preprocessed_data.csv'):
    try:
        df = pd.read_csv(input_csv)
        df['IR'] = df['IR'].astype(float)
        df['BPM'] = df['BPM'].astype(float)
        df['Avg_BPM'] = df['Avg_BPM'].astype(float)
        df['GSR'] = df['GSR'].astype(float)
        df.to_csv(output_csv, index=False)
        print(f"Dados pré-processados salvos em {output_csv}")
    except Exception as e:
        print(f"Erro durante o pré-processamento de dados: {str(e)}")

if __name__ == "__main__":
    preprocess_data()
