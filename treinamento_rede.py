import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

class TrainModelThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, csv_files):
        super().__init__()
        self.csv_files = csv_files

    def run(self):
        try:
            # Lendo os arquivos CSV e combinando-os
            dataframes = []
            for file in self.csv_files:
                if file:
                    df = pd.read_csv(file)
                    dataframes.append(df)
                    self.log_signal.emit(f"Arquivo {file} carregado com sucesso.")
            combined_df = pd.concat(dataframes)
            self.log_signal.emit("Dados combinados com sucesso.")

            # Preprocessamento dos dados
            X = combined_df[['irValue', 'beatsPerMinute', 'beatAvg', 'GSR']]
            y = combined_df['Content']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.log_signal.emit("Dados divididos em treino e teste.")

            # Treinamento do modelo
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            self.log_signal.emit("Modelo treinado com sucesso.")

            # Avaliação do modelo
            y_pred = model.predict(X_test)
            report = classification_report(y_test, y_pred)
            self.log_signal.emit(f"Relatório de classificação:\n{report}")

            # Salvando o modelo treinado
            joblib.dump(model, 'trained_model.pkl')
            self.log_signal.emit("Modelo salvo como 'trained_model.pkl'.")
        except Exception as e:
            self.log_signal.emit(f"Erro durante o treinamento do modelo: {str(e)}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.upload_buttons = []
        for i in range(5):
            button = QPushButton(f'Importar CSV {i+1}', self)
            button.clicked.connect(lambda checked, idx=i: self.import_csv(idx))
            self.upload_buttons.append(button)
            layout.addWidget(button)

        self.train_button = QPushButton('Treinar Rede', self)
        self.train_button.clicked.connect(self.train_model)
        self.train_button.setEnabled(False)
        layout.addWidget(self.train_button)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle('Treinamento de Rede')
        self.show()

        self.csv_files = [None] * 5

    def import_csv(self, index):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Importar CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file:
            self.csv_files[index] = file
            self.output.append(f"Arquivo CSV {index+1} selecionado: {file}")
            if any(self.csv_files):
                self.train_button.setEnabled(True)

    def train_model(self):
        self.output.append("Iniciando treinamento da rede...")
        self.train_button.setEnabled(False)

        valid_files = [file for file in self.csv_files if file is not None]
        self.train_thread = TrainModelThread(valid_files)
        self.train_thread.log_signal.connect(self.log_output)
        self.train_thread.start()

    def log_output(self, message):
        self.output.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
