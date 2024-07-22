import sys
import pandas as pd
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QTextEdit, QSpinBox, QProgressBar, QDialog, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from joblib import load

class DataCollectionThread(QThread):
    log_signal = pyqtSignal(str)
    data_signal = pyqtSignal(list)
    progress_signal = pyqtSignal(int)

    def __init__(self, port, duration):
        super().__init__()
        self.port = port
        self.duration = duration
        self.collecting = True

    def run(self):
        try:
            ser = serial.Serial(self.port, 115200)
            collected_data = []
            start_time = pd.Timestamp.now()
            while (pd.Timestamp.now() - start_time).seconds < self.duration:
                data = ser.readline().decode('utf-8').strip()
                self.log_signal.emit(data)
                data_split = data.split(',')
                if len(data_split) == 4:
                    collected_data.append([float(data_split[0]), float(data_split[1]), float(data_split[2]), float(data_split[3])])
                elapsed_time = (pd.Timestamp.now() - start_time).seconds
                progress = int((elapsed_time / self.duration) * 100)
                self.progress_signal.emit(progress)
            self.data_signal.emit(collected_data)
            ser.close()
        except Exception as e:
            self.log_signal.emit(f"Erro durante a coleta de dados: {str(e)}")

class PredictionThread(QThread):
    log_signal = pyqtSignal(str)
    prediction_signal = pyqtSignal(str)

    def __init__(self, model, data):
        super().__init__()
        self.model = model
        self.data = data

    def run(self):
        try:
            df = pd.DataFrame(self.data, columns=['irValue', 'beatsPerMinute', 'beatAvg', 'GSR'])
            predictions = self.model.predict(df)
            prediction_counts = pd.Series(predictions).value_counts()
            most_common = prediction_counts.idxmax()
            result_message = f"Tipo de conteúdo previsto: {most_common}"
            self.prediction_signal.emit(result_message)
            self.log_signal.emit(result_message)
        except Exception as e:
            self.log_signal.emit(f"Erro durante a previsão: {str(e)}")

class PredictionResultDialog(QDialog):
    def __init__(self, message):
        super().__init__()
        self.setWindowTitle("Resultado da Previsão")
        layout = QVBoxLayout()
        self.label = QLabel(message)
        layout.addWidget(self.label)
        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.port_label = QLabel("Selecione a Porta Serial:")
        layout.addWidget(self.port_label)

        self.port_combo = QComboBox(self)
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)
        layout.addWidget(self.port_combo)

        self.duration_label = QLabel("Selecione a duração da coleta (minutos):")
        layout.addWidget(self.duration_label)

        self.duration_spin = QSpinBox(self)
        self.duration_spin.setRange(1, 5)
        layout.addWidget(self.duration_spin)

        self.collect_button = QPushButton('Iniciar Coleta', self)
        self.collect_button.clicked.connect(self.collect_data)
        layout.addWidget(self.collect_button)

        self.predict_button = QPushButton('Previsão de Conteúdo', self)
        self.predict_button.clicked.connect(self.predict_content)
        self.predict_button.setEnabled(False)
        layout.addWidget(self.predict_button)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle('MindTV App')
        self.show()

    def get_selected_port(self):
        return self.port_combo.currentText()

    def get_duration(self):
        return self.duration_spin.value()

    def collect_data(self):
        port = self.get_selected_port()
        duration = self.get_duration() * 60  # Convert to seconds
        self.output.append(f"Iniciando coleta de dados na porta {port} por {self.get_duration()} minutos...")

        self.collect_button.setEnabled(False)
        self.data_collection_thread = DataCollectionThread(port, duration)
        self.data_collection_thread.log_signal.connect(self.log_output)
        self.data_collection_thread.data_signal.connect(self.save_data)
        self.data_collection_thread.progress_signal.connect(self.update_progress)
        self.data_collection_thread.start()

    def save_data(self, data):
        df = pd.DataFrame(data, columns=['irValue', 'beatsPerMinute', 'beatAvg', 'GSR'])
        df.to_csv('collected_data.csv', index=False)
        self.output.append("Dados coletados e salvos em collected_data.csv")
        self.collect_button.setEnabled(True)
        self.predict_button.setEnabled(True)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def predict_content(self):
        try:
            model = load('trained_model.joblib')
            data = pd.read_csv('collected_data.csv')
            self.prediction_thread = PredictionThread(model, data)
            self.prediction_thread.log_signal.connect(self.log_output)
            self.prediction_thread.prediction_signal.connect(self.show_prediction_result)
            self.prediction_thread.start()
        except Exception as e:
            self.output.append(f"Erro ao carregar modelo ou dados: {str(e)}")

    def show_prediction_result(self, message):
        dialog = PredictionResultDialog(message)
        dialog.exec_()

    def log_output(self, message):
        self.output.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
