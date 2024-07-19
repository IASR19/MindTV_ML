import sys
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QTextEdit, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
import time
import csv

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

        self.content_label = QLabel("Selecione o Tipo de Conteúdo:")
        layout.addWidget(self.content_label)

        self.content_combo = QComboBox(self)
        self.content_combo.addItems(["Reality Show", "Filme - Ação", "Filme - Drama", "Programa de Política", "Jornal"])
        layout.addWidget(self.content_combo)

        self.duration_label = QLabel("Duração da Coleta (segundos):")
        layout.addWidget(self.duration_label)

        self.duration_input = QLineEdit(self)
        self.duration_input.setText("120")
        layout.addWidget(self.duration_input)

        self.collect_button = QPushButton('Iniciar Coleta', self)
        self.collect_button.clicked.connect(self.collect_data)
        layout.addWidget(self.collect_button)

        self.export_button = QPushButton('Exportar CSV', self)
        self.export_button.clicked.connect(self.export_csv)
        layout.addWidget(self.export_button)
        self.export_button.setEnabled(False)

        self.output = QTextEdit(self)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle('Coleta Inicial')
        self.show()

    def get_selected_port(self):
        return self.port_combo.currentText()

    def get_duration(self):
        return int(self.duration_input.text())

    def get_content_type(self):
        return self.content_combo.currentText()

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
        self.export_button.setEnabled(True)

    def export_csv(self):
        content_type = self.get_content_type()
        filename = f'sensor_data_{content_type}.csv'
        try:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['IR', 'BPM', 'Avg_BPM', 'GSR'])
                writer.writerows(self.data)
            self.output.append(f"Dados salvos em {filename}")
        except Exception as e:
            self.output.append(f"Erro ao salvar CSV: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
