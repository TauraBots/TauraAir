import cv2
import numpy as np
from pyzbar.pyzbar import decode
from pyparrot.Minidrone import Mambo  # Controle do drone Parrot Mambo

# Inicializa a conexão com o drone (substitua pelo endereço correto do drone)
mamboAddr = "seu_endereco_drone"  # Exemplo: "d0:3a:bc:d7:e6:fc"
mambo = Mambo(mamboAddr, use_wifi=False)

# Tentativa de conexão ao drone
print("Conectando ao drone...")
if not mambo.connect(num_retries=3):
    print("Falha na conexão com o drone.")
    exit(1)

# Função para processar e interpretar o QR Code
def processa_qr_code(frame):
    decodifica_objetos = decode(frame)
    
    for obj in decodifica_objetos:
        qr_data = obj.data.decode('utf-8')
        print(f"Comando QR Code detectado: {qr_data}")

        # Executa movimentos do drone com base no comando do QR code
        if qr_data == "forward":
            print("Movendo para frente.")
            mambo.fly_direct(roll=0, pitch=30, yaw=0, vertical_movement=0, duration=1)
        elif qr_data == "backward":
            print("Movendo para trás.")
            mambo.fly_direct(roll=0, pitch=-30, yaw=0, vertical_movement=0, duration=1)
        elif qr_data == "left":
            print("Movendo para a esquerda.")
            mambo.fly_direct(roll=-30, pitch=0, yaw=0, vertical_movement=0, duration=1)
        elif qr_data == "right":
            print("Movendo para a direita.")
            mambo.fly_direct(roll=30, pitch=0, yaw=0, vertical_movement=0, duration=1)
        elif qr_data == "up":
            print("Subindo.")
            mambo.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=30, duration=1)
        elif qr_data == "down":
            print("Descendo.")
            mambo.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=-30, duration=1)
        elif qr_data == "land":
            print("Pousando drone.")
            mambo.safe_land()
            return True  # Retorna True para indicar que o pouso ocorreu

    return False  # Se não houver pouso, retorna False

# Função principal para processar o vídeo da câmera
def processar_camera_e_movimentar_drone():
    cap = cv2.VideoCapture(0)  # Usa a webcam como fonte de vídeo

    if not cap.isOpened():
        print("Erro ao acessar a câmera.")
        return

    mambo.safe_takeoff()  # O drone decola

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Processa o frame da câmera para decodificar QR codes
        if processa_qr_code(frame):
            # Se o comando for "land", a função processa_qr_code retorna True e o loop para
            break

        # Mostra o frame com QR code, se houver
        cv2.imshow("Detecção de QR Code", frame)

        # Pressione 'q' para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Executa o programa
try:
    processar_camera_e_movimentar_drone()
finally:
    mambo.safe_land()  # Pousa o drone com segurança
    mambo.disconnect()  # Desconecta do drone
