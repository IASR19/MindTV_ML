# Coleta de Dados de Sensores GSR e Frequência Cardíaca com Interface Gráfica

Este projeto permite a coleta de dados de sensores GSR (Galvanic Skin Response) e frequência cardíaca, pré-processamento, treinamento de modelo e previsão do tipo de conteúdo assistido na TV, através de uma interface gráfica.

## Pré-requisitos

- Python 3.6+
- PostgreSQL
- Bibliotecas Python:
  - PyQt5
  - numpy
  - pyserial
  - psycopg2
  - scikit-learn

## 1. Configuração do Banco de Dados

Instale o PostgreSQL e configure o banco de dados:

```bash
# Instalar PostgreSQL no macOS usando Homebrew
brew install postgresql

# Iniciar o serviço PostgreSQL
brew services start postgresql

# Conectar ao PostgreSQL
psql -U postgres

# Criar o banco de dados 'neurodata' e a tabela 'gsr_hr_data'
CREATE DATABASE neurodata;
\c neurodata
CREATE TABLE gsr_hr_data (
    participant_id INT,
    timestamp TIMESTAMP,
    ir_value FLOAT,
    bpm FLOAT,
    avg_bpm FLOAT,
    gsr_value FLOAT,
    current_video VARCHAR(255)
);

# Criar o ambiente virtual
python3 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate

# Instale as dependencias
pip install pyqt5 numpy pyserial psycopg2 scikit-learn

# Inicicar interface gráfica
python main.py
```
