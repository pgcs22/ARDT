# Exercício de análise de redes no domínio do tempo em que é simulado um curto-circuito
# utilizando o método MNA e integração trapezoidal

import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import Tk
import os

#dados do ATPDraw foram exportados em pl4 e convertidos para csv

def carregar_csv():

    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo CSV",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )

    root.destroy()


    try:
        with open(arquivo, 'r') as f:
            linhas = f.readlines()

        # Dados começam na 3 linha do csv
        dados_linhas = linhas[3:]

        tempo_csv = []
        corrente_csv = []

        for linha in dados_linhas:
            linha = linha.strip()
            if linha:
                partes = linha.split(',')
                if len(partes) >= 2:
                    try:
                        tempo = float(partes[0].strip())
                        corrente = float(partes[1].strip())
                        tempo_csv.append(tempo)
                        corrente_csv.append(corrente)
                    except ValueError:
                        continue

        tempo_csv = np.array(tempo_csv) * 1000  # Converter para ms
        corrente_csv = np.array(corrente_csv)

        print(f"Arquivo '{os.path.basename(arquivo)}' carregado com {len(tempo_csv)} pontos")
        return tempo_csv, corrente_csv

    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None

# Parâmetros
R1 = 0.5 #[Ohms]
L = 25E-3 #[H]
R2 = 20 #[Ohms]
dt = 1e-6 #[s]
tmax = 0.8 #[s]
N = int(tmax / dt) + 1

# Cálculo de Rl
Rl = (2 * L) / dt #[Ohms]

# inicialização da variável tempo
t = np.linspace(0, tmax, N)

# Termos da matriz
termo_11, termo_12, termo_13, termo_14, termo_15 = (1 / R1), (-1 / R1), 0, 1, 0
termo_21, termo_22, termo_23, termo_24, termo_25 = (-1 / R1), (1 / R1 + 1 / Rl), (-1 / Rl), 0, 0
termo_31, termo_32, termo_33, termo_34, termo_35 = 0, (-1 / Rl), (1 / R2 + 1 / Rl), 0, 1
termo_41, termo_42, termo_43, termo_44, termo_45 = 1, 0, 0, 0, 0
termo_51, termo_52, termo_53, termo_54, termo_55 = 0, 0, 0, 0, 1

termo_55b, termo_53b = 0, 1 # termos que se alteram no fechamento da chave

# Matriz da chave aberta (antes do curto-circuito)
G_aberta = np.array([
    [termo_11, termo_12, termo_13, termo_14, termo_15],
    [termo_21, termo_22, termo_23, termo_24, termo_25],
    [termo_31, termo_32, termo_33, termo_34, termo_35],
    [termo_41, termo_42, termo_43, termo_44, termo_45],
    [termo_51, termo_52, termo_53, termo_54, termo_55]
])

# Matriz da chave fechada (após curto circuito)
G_fechada = np.array([
    [termo_11, termo_12, termo_13, termo_14, termo_15],
    [termo_21, termo_22, termo_23, termo_24, termo_25],
    [termo_31, termo_32, termo_33, termo_34, termo_35],
    [termo_41, termo_42, termo_43, termo_44, termo_45],
    [termo_51, termo_52, termo_53b, termo_54, termo_55b]
])

# Condição inicial
Irp = 100 / (R1 + 1j * 377 * L + R2) # corrente em regime permanente
vrp = Irp * (377*L)
i_amp = np.abs(Irp)
i_fase = np.angle(Irp)
v_amp = np.abs(vrp)
v_fase = np.angle(vrp)
Il = i_amp * np.cos(i_fase) + (v_amp * np.cos(v_fase+377)/Rl)

# Simulação
I_array = np.zeros(N)


for n in range(N):
    vs = 100 * np.cos(377 * t[n])
    b = np.array([0, -Il, Il, vs, 0])# matriz de variáveis conhecidas
    G = G_aberta if t[n] < 0.08 else G_fechada
    x = np.linalg.solve(G, b)# resolução do sistema matricial
    V1, V2, V3, I, Is = x# matriz de incógnitas
    I_array[n] = -I
    Il = 2 * (V2 - V3) / Rl + Il# atualização do valor da corrente no indutor



#converter de microssegundos para milissegundos
t_ms = t * 1000

# Carregar CSV
dados_csv = carregar_csv()

# Criar gráfico
plt.figure(figsize=(12, 6))

# Plotar simulação
plt.plot(t_ms, I_array, 'b-', linewidth=1.5, label='Modelo Proposto')

# Plotar dados do CSV se disponível
if dados_csv:
    tempo_csv, corrente_csv = dados_csv
    plt.plot(tempo_csv, corrente_csv, 'r--', linewidth=1.5,
             label='Resultado ATPDraw', alpha=0.8)

plt.axvline(x=80, color='g', linestyle=':', linewidth=2, label='Curto-Circuito')
plt.xlabel('Tempo (ms)', fontsize=12)
plt.ylabel('Corrente (A)', fontsize=12)
plt.title('Comparação: Modelo criado x ATPDraw', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)
plt.xlim([0, tmax * 1000])

plt.show()