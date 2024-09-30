import cv2
from pyzbar.pyzbar import decode
import datetime

# Função para processar e interpretar o código de barras e salvar no arquivo
def processa_codigo_de_barras(frame, arquivo_saida):
    codigos_de_barras = decode(frame)
    
    for codigo in codigos_de_barras:
        # Decodifica os dados do código de barras
        codigo_data = codigo.data.decode('utf-8')
        print(f"Código de Barras detectado: {codigo_data}")

        # Salva o dado detectado no arquivo de texto com data e hora
        with open(arquivo_saida, 'a') as f:
            f.write(f"{datetime.datetime.now()}: Código de Barras detectado: {codigo_data}\n")

        # Desenha o contorno ao redor do código de barras
        pontos = codigo.polygon
        if len(pontos) == 4:
            pts = np.array(pontos, dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
        
        # Exibe o dado do código de barras na imagem
        cv2.putText(frame, codigo_data, (pontos[0].x, pontos[0].y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame

# Função principal para capturar o vídeo da câmera e ler códigos de barras
def processar_camera():
    cap = cv2.VideoCapture(0)  # Usa a webcam como fonte de vídeo
    arquivo_saida = 'codigos_detectados.txt'

    if not cap.isOpened():
        print("Erro ao acessar a câmera.")
        return

    # Cria ou limpa o arquivo de saída
    with open(arquivo_saida, 'w') as f:
        f.write("Histórico de Códigos de Barras Detectados:\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Processa o frame da câmera para decodificar códigos de barras
        frame = processa_codigo_de_barras(frame, arquivo_saida)

        # Mostra o frame com o código de barras detectado, se houver
        cv2.imshow("Leitura de Código de Barras", frame)

        # Pressione 'q' para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Executa o programa
processar_camera()
