import sys
import serial
import psycopg2
import time

def save_gsr_hr_data(participant_id, ir_value, bpm, avg_bpm, gsr_value, current_video):
    conn = psycopg2.connect(dbname='neurodata', user='postgres', password='yourpassword', host='localhost')
    cursor = conn.cursor()
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO gsr_hr_data (participant_id, timestamp, ir_value, bpm, avg_bpm, gsr_value, current_video) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (participant_id, timestamp, ir_value, bpm, avg_bpm, gsr_value, current_video))
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    port = sys.argv[1]
    current_video = sys.argv[2]
    ser = serial.Serial(port, 115200)  # Ajuste a porta conforme necessário
    participant_id = 1  # ID do participante

    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            values = line.split(',')
            if len(values) == 4:
                ir_value, bpm, avg_bpm, gsr_value = map(float, values)
                save_gsr_hr_data(participant_id, ir_value, bpm, avg_bpm, gsr_value, current_video)
            else:
                print(f"Received an incomplete line: {line}")
