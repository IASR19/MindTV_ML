from builtins import Exception, range, str, super
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from joblib import dump

class TrainingThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        try:
            dfs = []
            for file_path in self.file_paths:
                if file_path:
                    df = pd.read_csv(file_path)
                    if 'Content' not in df.columns:
                        self.log_signal.emit(f"Erro: o arquivo {file_path} não contém a coluna 'Content'.")
                        return
                    dfs.append(df)
            data = pd.concat(dfs, ignore_index=True)
            X = data[['irValue', 'beatsPerMinute', 'beatAvg', 'GSR']]
            y = data['Content']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            dump(model, 'trained_model.joblib')
            self.log_signal.emit("Treinamento concluído e modelo salvo como 'trained_model.joblib'.")
        except Exception as e:
            self.log_signal.emit(f"Erro durante o treinamento: {str(e)}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.import_buttons = []
        for i in range(5):
            import_button = QPushButton(f'Selecionar arquivo CSV {i+1}', self)
            import_button.clicked.connect(lambda _, x=i: self.import_csv(x))
            layout.addWidget(import_button)
            self.import_buttons.append(import_button)

        self.train_button = QPushButton('Treinar Modelo', self)
        self.train_button.clicked.connect(self.train_model)
        layout.addWidget(self.train_button)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle('Treinamento da Rede')
        self.show()

        self.file_paths = [None] * 5

    def import_csv(self, index):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            self.file_paths[index] = file_path
            self.output.append(f"Arquivo {index+1} selecionado: {file_path}")

    def train_model(self):
        if not self.file_paths[0]:
            self.output.append("Erro: pelo menos um arquivo CSV deve ser selecionado.")
            return
        self.output.append("Iniciando o treinamento do modelo...")
        self.train_button.setEnabled(False)
        self.training_thread = TrainingThread(self.file_paths)
        self.training_thread.log_signal.connect(self.log_output)
        self.training_thread.start()

    def log_output(self, message):
        self.output.append(message)
        self.train_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())