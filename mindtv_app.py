import sys
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QTextEdit, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
import joblib
import pandas as pd
import time

class DataCollectionThread(QThread):
    log_signal = pyqtSignal(str)
    data_signal = pyqtSignal(list)

    def __init__(self, port, duration):
        super().__init__()
        self.port = port
        self.duration = duration

    def run(self):
        try:
            ser = serial.Serial(self.port, 115200)
            ser.write(b'L')
            start_time = time.time()
            data = []
            while time.time() - start_time < self.duration:
                line = ser.readline().decode('utf-8').strip()
                data.append(line.split(','))
                self.log_signal.emit(line)
            ser.write(b'D')
            ser.close()
            self.data_signal.emit(data)
            self.log_signal.emit("Coleta de dados concluída.")
        except Exception as e:
            self.log_signal.emit(f"Erro durante a coleta de dados: {str(e)}")

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

        self.duration_label = QLabel("Duração da Coleta (segundos):")
        layout.addWidget(self.duration_label)

        self.duration_input = QLineEdit(self)
        self.duration_input.setText("120")
        layout.addWidget(self.duration_input)

        self.collect_button = QPushButton('Coletar Dados', self)
        self.collect_button.clicked.connect(self.collect_data)
        layout.addWidget(self.collect_button)

        self.predict_button = QPushButton('Previsão de Conteúdo', self)
        self.predict_button.clicked.connect(self.predict_content)
        self.predict_button.setEnabled(False)
        layout.addWidget(self.predict_button)

        self.export_button = QPushButton('Exportar Resultado', self)
        self.export_button.clicked.connect(self.export_result)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)

        self.output = QTextEdit(self)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle('MindTV App')
        self.show()

    def get_selected_port(self):
        return self.port_combo.currentText()

    def get_duration(self):
        return int(self.duration_input.text())

    def collect_data(self):
        port = self.get_selected_port()
        duration = self.get_duration()
        self.output.append(f"Iniciando coleta de dados na porta {port} por {duration} segundos...")

        self.data_collection_thread = DataCollectionThread(port, duration)
        self.data_collection_thread.log_signal.connect(self.log_output)
        self.data_collection_thread.data_signal.connect(self.store_data)
        self.data_collection_thread.start()

    def log_output(self, message):
        self.output.append(message)

    def store_data(self, data):
        self.data = data
        self.predict_button.setEnabled(True)
        self.output.append("Coleta de dados armazenada.")

    def predict_content(self):
        try:
            model = joblib.load('trained_model.pkl')
            df = pd.DataFrame(self.data, columns=['IR', 'BPM', 'Avg_BPM', 'GSR'])
            df = df.astype(float)
            predictions = model.predict(df)
            prediction = pd.Series(predictions).mode()[0]  # Getting the most frequent prediction
            self.output.append(f"Previsão do tipo de conteúdo: {prediction}")
            self.result = prediction
            self.export_button.setEnabled(True)
        except Exception as e:
            self.output.append(f"Erro durante a previsão: {str(e)}")

    def export_result(self):
        try:
            with open('prediction_result.txt', 'w') as file:
                file.write(f"Previsão do tipo de conteúdo: {self.result}\n")
                file.write("Dados da coleta:\n")
                for line in self.data:
                    file.write(f"{','.join(line)}\n")
            self.output.append("Resultado exportado para prediction_result.txt")
        except Exception as e:
            self.output.append(f"Erro ao exportar resultado: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
