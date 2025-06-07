# AOOP-ComputerVision

# Aplicação de Desenho com Gestos da Mão (OpenCV + MediaPipe)

Esta aplicação permite desenhar, apagar, mudar de cor e guardar desenhos usando apenas gestos das mãos capturados pela webcam. Utiliza as bibliotecas **OpenCV** e **MediaPipe** para visão computacional em tempo real.

## 🛠 Tecnologias Utilizadas

- **OpenCV** – Para captura de vídeo, manipulação de imagem e interface visual.
- **MediaPipe (Hands)** – Para detecção e rastreamento dos pontos da mão.

## ✋ Gestos Suportados

| Gesto                    | Ação                     |
|--------------------------|--------------------------|
| 1 dedo (indicador)       | Desenhar                 |
| 2 dedos (indicador + médio) | Apagar com "borracha"     |
| 3 dedos                  | Mudar a cor do pincel    |
| 5 dedos abertos          | Guardar o desenho        |


> Ao guardar, duas imagens são criadas: o desenho isolado e a imagem da webcam com o desenho sobreposto.


## Como Funciona

1. A aplicação tenta automaticamente encontrar uma webcam disponível nos índices 0 a 2.
2. Ao iniciar, abre uma janela onde o utilizador pode interagir com a câmara.
3. O utilizador controla a pintura no ecrã através de gestos da mão reconhecidos pelo MediaPipe.

## ▶️ Como Executar

1. Certifica-te de ter Python 3 instalado. (versão 3.12.0 foi usada durante o desenvolvimento)
2. Instala as dependências:
```bash
pip install opencv-python mediapipe numpy
```
3. Execute o ficheiro vpaint.py
```bash
python vpaint.py
```