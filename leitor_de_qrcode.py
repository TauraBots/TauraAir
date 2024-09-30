import cv2
import numpy as np
from pyzbar.pyzbar import decode

# Caminho do arquivo do modelo
prototxt = 'deploy.prototxt'
model = 'mobilenet_iter_73000.caffemodel'

# Carrega a rede neural MobileNet SSD
# https://insper.github.io/robotica-computacional/modulos/06-visao-p3/atividades/1-mobilenet/
net = cv2.dnn.readNetFromCaffe(prototxt, model)

# Definir classes
CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant",
    "sheep", "sofa", "train", "tvmonitor"
]

# Funções
def processa_qr_code(frame, output_file):
    decodifica_objetos = decode(frame)
    for obj in decodifica_objetos:
        pontos = obj.polygon
        if len(pontos) == 4:
            pts = np.array(pontos, dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)  # Correção: cv2.polynes -> cv2.polylines
            qr_data = obj.data.decode('utf-8')
            cv2.putText(frame, qr_data, (pts[0][0], pts[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            with open(output_file, 'a') as f:  # Correção: ';' -> ':'
                f.write(f"QR Code Data: {qr_data}\n")

def processar_camera_e_gravar(arquivo_de_saida):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro ao abrir a webcam")
        return

    with open(arquivo_de_saida, 'w') as f:
        f.write("Detecções:\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        (altura, largura) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        deteccao = net.forward()

        for i in range(deteccao.shape[2]):
            probabilidade = deteccao[0, 0, i, 2]
            if probabilidade > 0.2:
                box = deteccao[0, 0, i, 3:7] * np.array([largura, altura, largura, altura])  # Correção: idx -> box
                (iniciaX, iniciaY, finalizaX, finalizaY) = box.astype("int")
                idx = int(deteccao[0, 0, i, 1])  # Correção: identificador da classe (idx)
                label = f"{CLASSES[idx]}: {probabilidade:.2f}"
                cv2.rectangle(frame, (iniciaX, iniciaY), (finalizaX, finalizaY), (0, 255, 0), 2)
                cv2.putText(frame, label, (iniciaX, iniciaY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                with open(arquivo_de_saida, 'a') as f:
                    f.write(f"Detectado: {label} às [{iniciaX}, {iniciaY}, {finalizaX}, {finalizaY}]\n")

        processa_qr_code(frame, arquivo_de_saida)

        cv2.imshow("Detecção de Objetos e Código QR", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Arquivo de saída para as detecções e códigos QR
arquivo_de_saida = 'detecoes_e_codigos_qr.txt'
processar_camera_e_gravar(arquivo_de_saida)
