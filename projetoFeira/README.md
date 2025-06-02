# Projeto Detector de Flexões

Este projeto utiliza a webcam para detectar e contar flexões de braço em tempo real, utilizando MediaPipe para estimativa de pose e OpenCV para processamento de imagem.

## Funcionalidades

- Detecção de landmarks do corpo (ombros, cotovelos, pulsos).
- Cálculo do ângulo do cotovelo para determinar o estágio da flexão (estendido/flexionado).
- Contagem de repetições.
- Calibração inicial para ajustar os ângulos de flexão e extensão com base no usuário.
- Feedback visual na tela (ângulo atual, número de repetições, mensagens de instrução).
- Seleção do braço a ser monitorado (direito ou esquerdo).
- Interface em tela cheia.

## Como Executar

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd projetoFeira
    ```

2.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o script principal:**
    ```bash
    python main.py
    ```

    - Siga as instruções no terminal para selecionar o braço a ser monitorado.
    - Realize os movimentos de calibração conforme solicitado.
    - Pressione 'p' para pausar/retomar e 'q' para sair.

## Dependências

As dependências do projeto estão listadas no arquivo `requirements.txt` e podem ser instaladas com:

```bash
pip install -r requirements.txt
```

Principais bibliotecas utilizadas:

-   **OpenCV (`cv2`)**: Para captura e processamento de vídeo/imagem.
-   **NumPy**: Para cálculos numéricos, especialmente com ângulos.
-   **MediaPipe**: Para a detecção de pose e landmarks corporais.

## Estrutura do Projeto

```
projetoFeira/
├── assets/
│   └── images/           # (Opcional) Para imagens estáticas, se houver
├── config/
│   └── settings.py       # Configurações como ângulos padrão, repetições de calibração
├── data/                   # (Opcional) Para dados, se houver
├── main.py                 # Ponto de entrada principal da aplicação
├── requirements.txt        # Lista de dependências Python
├── README.md               # Este arquivo
└── utils/
    ├── __init__.py
    ├── angle_calculator.py # Lógica para calcular ângulos
    └── pose_estimator.py   # Lógica para estimativa de pose com MediaPipe
```

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.