import serial
import time
import csv

def collect_data(port, duration=120):
    try:
        ser = serial.Serial(port, 115200)
        ser.write(b'L')
        start_time = time.time()
        data = []
        while time.time() - start_time < duration:
            line = ser.readline().decode('utf-8').strip()
            data.append(line.split(','))
            print(line)
        ser.write(b'D')
        ser.close()
        return data
    except Exception as e:
        print(f"Erro durante a coleta de dados: {str(e)}")
        return []

def save_to_csv(data, filename='sensor_data.csv'):
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['IR', 'BPM', 'Avg_BPM', 'GSR'])
            writer.writerows(data)
        print(f"Dados salvos em {filename}")
    except Exception as e:
        print(f"Erro ao salvar CSV: {str(e)}")

if __name__ == "__main__":
    port = input("Digite a porta serial: ")
    data = collect_data(port)
    save_to_csv(data)
