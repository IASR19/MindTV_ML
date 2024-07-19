import sys
import os
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QTextEdit, QLineEdit
from subprocess import Popen, PIPE
import numpy as np  # Certifique-se de importar numpy

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.serial_port = None
        self.participant_id = 1

    def initUI(self):
        layout = QVBoxLayout()

        # Porta Serial
        self.port_label = QLabel("Selecione a Porta Serial:")
        layout.addWidget(self.port_label)

        self.port_combo = QComboBox(self)
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)
        layout.addWidget(self.port_combo)

        # Input do Vídeo Atual
        self.video_label = QLabel("Digite o ID do Vídeo:")
        layout.addWidget(self.video_label)
        self.video_input = QLineEdit(self)
        layout.addWidget(self.video_input)

        # Botões
        self.collect_button = QPushButton('Iniciar Coleta', self)
        self.collect_button.clicked.connect(self.collect_data)
        layout.addWidget(self.collect_button)

        self.preprocess_button = QPushButton('Pré-processar Dados', self)
        self.preprocess_button.clicked.connect(self.preprocess_data)
        layout.addWidget(self.preprocess_button)

        self.train_button = QPushButton('Treinar Modelo', self)
        self.train_button.clicked.connect(self.train_model)
        layout.addWidget(self.train_button)

        self.predict_button = QPushButton('Prever Programa de TV', self)
        self.predict_button.clicked.connect(self.predict_tv_show)
        layout.addWidget(self.predict_button)

        self.output = QTextEdit(self)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle('Interface de Coleta e Previsão')
        self.show()

    def get_selected_port(self):
        return self.port_combo.currentText()

    def collect_data(self):
        port = self.get_selected_port()
        current_video = self.video_input.text()
        self.output.append(f"Iniciando coleta de dados na porta {port} para o vídeo {current_video}...")

        # Executar script de coleta
        gsr_process = Popen([sys.executable, 'collect_gsr_hr_data.py', port, current_video], stdout=PIPE, stderr=PIPE)
        
        stdout_gsr, stderr_gsr = gsr_process.communicate()
        
        self.output.append(stdout_gsr.decode())
        self.output.append(stderr_gsr.decode())

        self.output.append("Coleta de dados concluída!")

    def preprocess_data(self):
        self.output.append("Pré-processando dados...")
        process = Popen([sys.executable, 'preprocess_data.py'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        self.output.append(stdout.decode())
        self.output.append(stderr.decode())
        self.output.append("Pré-processamento concluído!")

    def train_model(self):
        self.output.append("Treinando modelo...")
        process = Popen([sys.executable, 'train_model.py'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        self.output.append(stdout.decode())
        self.output.append(stderr.decode())
        self.output.append("Treinamento do modelo concluído!")

    def predict_tv_show(self):
        self.output.append("Prevendo programa de TV...")
        # Aqui você pode adicionar o código para carregar o modelo treinado e fazer previsões
        import pickle
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        # Simulação de dados para previsão
        simulated_data = np.array([[0.5, 0.6, 0.7, 0.8]])
        prediction = model.predict(simulated_data)
        self.output.append(f"Previsão: {prediction[0]}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
