from builtins import Exception, int, list, str, super
import sys
import time
import os
import pandas as pd
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal

class DataCollectionThread(QThread):
    log_signal = pyqtSignal(str)
    data_signal = pyqtSignal(list)

    def __init__(self, port, duration):
        super().__init__()
        self.port = port
        self.duration = duration
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, 115200)
            self.log_signal.emit("Iniciando coleta de dados...")
            start_time = time.time()
            data = []
            while time.time() - start_time < self.duration:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    if ',' in line:
                        irValue, beatsPerMinute, beatAvg, GSR = line.split(',')
                        data.append([irValue, beatsPerMinute, beatAvg, GSR])
                        self.log_signal.emit(f"IR: {irValue}, BPM: {beatsPerMinute}, Avg BPM: {beatAvg}, GSR: {GSR}")
            self.ser.close()
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

        self.duration_label = QLabel("Tempo de Coleta (minutos):")
        layout.addWidget(self.duration_label)

        self.duration_combo = QComboBox(self)
        self.duration_combo.addItems(["1", "2", "3", "4", "5"])
        layout.addWidget(self.duration_combo)

        self.content_label = QLabel("Tipo de Conteúdo Assistido:")
        layout.addWidget(self.content_label)

        self.content_combo = QComboBox(self)
        self.content_combo.addItems(["Reality Show", "Filme de Ação", "Filme de Comédia", "Programa de Política", "Jornal"])
        layout.addWidget(self.content_combo)

        self.collect_button = QPushButton('Iniciar Coleta', self)
        self.collect_button.clicked.connect(self.collect_data)
        layout.addWidget(self.collect_button)

        self.export_button = QPushButton('Exportar CSV', self)
        self.export_button.clicked.connect(self.export_csv)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)  # Torna o campo de log somente leitura
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle('Coleta Inicial')
        self.show()

    def get_selected_port(self):
        return self.port_combo.currentText()

    def get_selected_duration(self):
        return int(self.duration_combo.currentText()) * 60

    def collect_data(self):
        port = self.get_selected_port()
        duration = self.get_selected_duration()
        self.output.append(f"Iniciando coleta de dados na porta {port} por {duration // 60} minutos...")
        self.collect_button.setEnabled(False)  # Desabilita o botão após ser clicado

        self.data_collection_thread = DataCollectionThread(port, duration)
        self.data_collection_thread.log_signal.connect(self.log_output)
        self.data_collection_thread.data_signal.connect(self.store_data)
        self.data_collection_thread.start()

    def log_output(self, message):
        self.output.append(message)

    def store_data(self, data):
        self.data = data
        self.export_button.setEnabled(True)
        self.collect_button.setEnabled(True)  # Reabilita o botão após a coleta ser concluída
        self.output.append("Coleta de dados armazenada.")

    def export_csv(self):
        try:
            df = pd.DataFrame(self.data, columns=['irValue', 'beatsPerMinute', 'beatAvg', 'GSR'])
            content_type = self.content_combo.currentText()
            df['Content'] = content_type

            # Verificar se já existe um arquivo com o mesmo nome e ajustar o nome do arquivo se necessário
            base_filename = 'coleta_dados'
            extension = '.csv'
            filename = base_filename + extension
            counter = 1
            while os.path.exists(filename):
                filename = f"{base_filename}({counter}){extension}"
                counter += 1

            df.to_csv(filename, index=False)
            self.output.append(f"Dados exportados para {filename}")
        except Exception as e:
            self.output.append(f"Erro ao exportar dados: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())