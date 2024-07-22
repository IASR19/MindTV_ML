from builtins import Exception, float, int, len, list, str, super
import sys
import os
import pandas as pd
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QTextEdit, QSpinBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from joblib import load
import time

class DataCollectionThread(QThread):
    log_signal = pyqtSignal(str)
    data_signal = pyqtSignal(list)
    update_timer_signal = pyqtSignal(int)

    def __init__(self, port, duration):
        super().__init__()
        self.port = port
        self.duration = duration
        self.collecting = True

    def run(self):
        try:
            ser = serial.Serial(self.port, 115200)
            collected_data = []
            start_time = time.time()
            elapsed_time = 0
            while self.collecting and elapsed_time < self.duration:
                elapsed_time = time.time() - start_time
                data = ser.readline().decode('utf-8').strip()
                self.log_signal.emit(data)
                data_split = data.split(',')
                if len(data_split) == 4:
                    collected_data.append([float(data_split[0]), float(data_split[1]), float(data_split[2]), float(data_split[3])])
                self.update_timer_signal.emit(int(elapsed_time))
            self.data_signal.emit(collected_data)
            ser.close()
        except Exception as e:
            self.log_signal.emit(f"Erro durante a coleta de dados: {str(e)}")

    def stop(self):
        self.collecting = False

class PredictionThread(QThread):
    log_signal = pyqtSignal(str)

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
            self.log_signal.emit(f"Tipo de conteúdo previsto: {most_common}")
        except Exception as e:
            self.log_signal.emit(f"Erro durante a previsão: {str(e)}")

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

        self.timer_label = QLabel("Tempo decorrido: 0 segundos")
        layout.addWidget(self.timer_label)

        self.collect_button = QPushButton('Iniciar Coleta', self)
        self.collect_button.clicked.connect(self.collect_data)
        layout.addWidget(self.collect_button)

        self.predict_button = QPushButton('Previsão de Conteúdo', self)
        self.predict_button.clicked.connect(self.predict_content)
        layout.addWidget(self.predict_button)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle('MindTV App')
        self.show()

    def get_selected_port(self):
        return self.port_combo.currentText()

    def get_duration(self):
        return self.duration_spin.value() * 60  # Convert to seconds

    def collect_data(self):
        port = self.get_selected_port()
        duration = self.get_duration()  # Duration in seconds
        self.output.append(f"Iniciando coleta de dados na porta {port} por {self.get_duration() // 60} minutos...")

        self.collect_button.setEnabled(False)
        self.data_collection_thread = DataCollectionThread(port, duration)
        self.data_collection_thread.log_signal.connect(self.log_output)
        self.data_collection_thread.data_signal.connect(self.save_data)
        self.data_collection_thread.update_timer_signal.connect(self.update_timer)
        self.data_collection_thread.start()

    def update_timer(self, elapsed_time):
        self.timer_label.setText(f"Tempo decorrido: {elapsed_time} segundos")

    def save_data(self, data):
        df = pd.DataFrame(data, columns=['irValue', 'beatsPerMinute', 'beatAvg', 'GSR'])
        df.to_csv('collected_data.csv', index=False)
        self.output.append("Dados coletados e salvos em collected_data.csv")
        self.collect_button.setEnabled(True)

    def predict_content(self):
        try:
            model = load('trained_model.joblib')
            data = pd.read_csv('collected_data.csv')
            prediction_thread = PredictionThread(model, data)
            prediction_thread.log_signal.connect(self.log_output)
            prediction_thread.start()
        except Exception as e:
            self.output.append(f"Erro ao carregar modelo ou dados: {str(e)}")

    def log_output(self, message):
        self.output.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
