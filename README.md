# Projeto MindTV

O projeto MindTV consiste em três interfaces gráficas distintas que realizam diferentes etapas no processo de coleta, treinamento e previsão de dados de sensores de GSR e frequência cardíaca.

## 1. Coleta Inicial (`coleta_inicial.py`)

Esta interface realiza a coleta dos dados de sensores GSR e frequência cardíaca conectados a um Arduino.

### Funcionalidades:
- Escolha da porta serial.
- Escolha do tipo de conteúdo sendo assistido.
- Definição do tempo de coleta (1 a 5 minutos).
- Exibição em tempo real dos dados coletados.
- Exportação dos dados coletados em um arquivo CSV.

### Como usar:
1. Execute a interface gráfica:
   ```bash
   python coleta_inicial.py

2. Selecione a porta serial à qual o Arduino está conectado.
3. Selecione o tipo de conteúdo que está sendo assistido.
4. Defina o tempo de coleta entre 1 a 5 minutos.
5. Clique em "Iniciar Coleta" para começar a coleta dos dados.
6. Acompanhe os dados em tempo real na área de log.
7. Clique em "Exportar CSV" para salvar os dados coletados em um arquivo CSV.

## 2. Treinamento da Rede (`treinamento_rede.py`)

Esta interface permite importar arquivos CSV gerados pela primeira interface para treinar um modelo de machine learning que reconhece o tipo de conteúdo assistido.

### Funcionalidades:
- Importação de até 5 arquivos CSV (1 obrigatório e 4 opcionais).
- Treinamento do modelo de machine learning com base nos dados importados.
- Exibição de barra de progresso durante o treinamento.
- Exibição de logs de progresso e resultados do treinamento.
- Botão "Concluído" ativado após o término do treinamento.

### Como usar:
1. Execute a interface gráfica:
   ```bash
   python treinamento_rede.py

2. Na interface, clique nos botões para importar os arquivos CSV necessários:
- O primeiro campo de importação é obrigatório.
- Os outros quatro campos são opcionais.
3. Após importar os arquivos CSV, clique no botão "Treinar Rede" para iniciar o processo de treinamento.
4. Acompanhe a barra de progresso e os logs de treinamento exibidos na interface.
5. Quando o treinamento for concluído, o botão "Concluído" será ativado, indicando que o modelo está pronto para uso.

## 3. Aplicativo MindTV (`mindtv_app.py`)

Esta interface permite a coleta de novos dados, previsão do tipo de conteúdo assistido usando o modelo treinado e exportação dos resultados.

### Funcionalidades:
- Escolha da porta serial.
- Definição do tempo de coleta (1 a 5 minutos).
- Coleta de novos dados dos sensores GSR e frequência cardíaca.
- Previsão do tipo de conteúdo assistido com base nos dados coletados.
- Exibição de logs e resultados em tempo real.
- Exportação dos resultados da previsão em um arquivo CSV.

### Como usar:
1. Execute a interface gráfica:
   ```bash
   python mindtv_app.py
2. Na interface, selecione a porta serial à qual o Arduino está conectado.
3. Defina o tempo de coleta entre 1 a 5 minutos.
4. Clique em "Coletar Dados" para iniciar a coleta dos dados dos sensores.
5. Após a coleta, clique em "Previsão de Conteúdo" para prever o tipo de conteúdo assistido.
6. Acompanhe os dados e resultados em tempo real na área de log.
7. Clique em "Exportar Resultado" para salvar os dados e previsões em um arquivo CSV.

# Dependências e Instalação

## Dependências

Para o funcionamento correto do projeto MindTV, são necessárias as seguintes dependências:

- Python 3.x
- pandas
- scikit-learn
- PyQt5
- pyserial

## Instalação das Dependências

### Passo a Passo

1. **Certifique-se de que o Python 3.x está instalado:**
   Para verificar se o Python está instalado em seu sistema, você pode executar o seguinte comando no terminal:
   ```bash
   python --version

2. Crie um ambiente virtual (opcional, mas recomendado):
Para evitar conflitos entre pacotes, é recomendável criar um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate
````
3. Instale as dependências:
```bash
pip install -r requirements.txt
