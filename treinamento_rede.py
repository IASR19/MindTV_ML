import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

class TrainingThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, csv_files):
        super().__init__()
        self.csv_files = csv_files

    def run(self):
        try:
            dataframes = [pd.read_csv(csv_file) for csv_file in self.csv_files]
            df = pd.concat(dataframes)

            X = df[['IR', 'BPM', 'Avg_BPM', 'GSR']]
            y = df['Label']

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            predictions = model.predict(X_test)
            report = classification_report(y_test, predictions)
            self.log_signal.emit(report)

            joblib.dump(model, 'trained_model.pkl')
            self.log_signal.emit("Modelo salvo em trained_model.pkl")
        except Exception as e:
            self.log_signal.emit(f"Erro durante o treinamento do modelo: {str(e)}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.import_button = QPushButton('Importar CSV', self)
        self.import_button.clicked.connect(self.import_csv)
        layout.addWidget(self.import_button)

        self.train_button = QPushButton('Treinar Rede', self)
        self.train_button.clicked.connect(self.train_model)
        self.train_button.setEnabled(False)
        layout.addWidget(self.train_button)

        self.output = QTextEdit(self)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle('Treinamento de Rede')
        self.show()

    def import_csv(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Importar CSVs", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if files:
            self.csv_files = files
            self.output.append(f"Arquivos CSV importados: {', '.join(files)}")
            self.train_button.setEnabled(True)

    def train_model(self):
        self.output.append("Iniciando treinamento da rede...")

        self.training_thread = TrainingThread(self.csv_files)
        self.training_thread.log_signal.connect(self.log_output)
        self.training_thread.start()

    def log_output(self, message):
        self.output.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
