# Exercício de análise de redes no domínio do tempo em que é simulado um modelo de transformador

import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import Tk
import os

# dados do ATPDraw foram exportados em pl4 e convertidos para csv

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
        return None, None

dt = 1e-6  # passo de tempo
tmax = 0.2  # tempo máximo
t = np.arange(0, tmax + dt, dt)
N = len(t)

E = 220 * np.sqrt(2)  # tensão da fonte
f = 60  # frequência
theta = 0  # ângulo inicial
vs = E * np.cos(2 * np.pi * f * t + theta * np.pi / 180)

# PARÂMETROS DO TRANSFORMADOR
R1 = 1
L1 = 0.3e-3
R2 = 0.3
L2 = 0.1e-3
RM = 5e3
n = 2
LM1 = 10  # região linear
LM2 = 47.6e-3  # saturado
lb0 = 1
C = 10e-6

RL1 = 2 * L1 / dt
RL2 = 2 * L2 / dt
RC = dt / (2 * C)

x = np.zeros(12)
lb = 0
v4_ant = 0
IL1 = 0
IL2 = 0
ILM = 0
IC = 0
RLM = 2 * LM1 / dt

is_current = np.zeros(N)  # Corrente da Fonte

for m in range(N):
    tempo = t[m]


    if abs(lb) <= lb0:
        LM = LM1
    else:
        LM = LM2

    RLM = 2 * LM / dt

    if tempo < 0.01:
        # CASO 1: s1 aberta, s2 fechada
        A = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0],
            [0, 1/R1, -1/R1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, -1/R1, (1/R1 + 1/RL1), -1/RL1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, -1/RL1, (1/RL1 + 1/RM + 1/RLM), 0, 0, 0, 0, 0, 0, 0, -1/n],
            [0, 0, 0, 0, 1/R2, -1/R2, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, -1/R2, (1/R2 + 1/RL2), -1/RL2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -1/RL2, 1/RL2, 0, 0, 0, -1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1/RC, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = vs
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # isw1 = 0 (chave 1 aberta)
            [0, 0, 0, 1, -n, 0, 0, 0, 0, 0, 0, 0],  # v4 - n*v5 = 0
            [0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0]   # v7 = v8 (chave 2 fechada)
        ])

    elif tempo >= 0.01 and tempo < 0.05:
        # CASO 2: s1 fechada, s2 fechada
        A = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0],
            [0, 1/R1, -1/R1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, -1/R1, (1/R1 + 1/RL1), -1/RL1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, -1/RL1, (1/RL1 + 1/RM + 1/RLM), 0, 0, 0, 0, 0, 0, 0, -1/n],
            [0, 0, 0, 0, 1/R2, -1/R2, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, -1/R2, (1/R2 + 1/RL2), -1/RL2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -1/RL2, 1/RL2, 0, 0, 0, -1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1/RC, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = vs
            [1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = v2 (chave 1 fechada)
            [0, 0, 0, 1, -n, 0, 0, 0, 0, 0, 0, 0],  # v4 - n*v5 = 0
            [0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0]   # v7 = v8 (chave 2 fechada)
        ])

    else:
        # CASO 3: s1 fechada, s2 aberta
        A = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0],
            [0, 1/R1, -1/R1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, -1/R1, (1/R1 + 1/RL1), -1/RL1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, -1/RL1, (1/RL1 + 1/RM + 1/RLM), 0, 0, 0, 0, 0, 0, 0, -1/n],
            [0, 0, 0, 0, 1/R2, -1/R2, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, -1/R2, (1/R2 + 1/RL2), -1/RL2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -1/RL2, 1/RL2, 0, 0, 0, -1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1/RC, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = vs
            [1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = v2 (chave 1 fechada)
            [0, 0, 0, 1, -n, 0, 0, 0, 0, 0, 0, 0],  # v4 - n*v5 = 0
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]   # isw2 = 0 (chave 2 aberta)
        ])

    # Vetor b corrigido - a ordem deve corresponder às equações
    b = np.array([
        0,           # nó 0
        0,           # nó 1
        -IL1,        # nó 2 - corrente histórica do indutor L1
        IL1 - ILM,   # nó 3
        0,           # nó 4
        -IL2,        # nó 5
        IL2,         # nó 6
        -IC,         # nó 7
        vs[m],       # nó 8 (fonte)
        0,           # equação da chave 1
        0,           # equação do transformador
        0            # equação da chave 2
    ])

    try:
        x = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        print(f"Erro: Matriz singular no tempo {tempo:.6f}s")
        x = np.linalg.lstsq(A, b, rcond=None)[0]

    # Extrair variáveis na ordem correta
    v1, v2, v3, v4, v5, v6, v7, v8, i1, i2, isw1, isw2 = x
    is_current[m] = -i1  # Corrente da fonte

    # Atualização das variáveis históricas
    lb = lb + (v4 + v4_ant) * dt / 2
    v4_ant = v4
    IL1 = 2 * (v3 - v4) / RL1 + IL1
    IL2 = 2 * (v6 - v7) / RL2 + IL2
    ILM = 2 * v4 / RLM + ILM
    IC = -2 * v8 / RC - IC

# Converter de segundos para milissegundos
t_ms = t * 1000

# Carregar CSV
dados_csv = carregar_csv()

# Criar gráfico
plt.figure(figsize=(12, 6))

# Plotar simulação
plt.plot(t_ms, is_current, 'b-', linewidth=1.5, label='Modelo Proposto')

# Plotar dados do CSV se disponível
if dados_csv[0] is not None:
    tempo_csv, corrente_csv = dados_csv
    plt.plot(tempo_csv, corrente_csv, 'r--', linewidth=1.5,
             label='Resultado ATPDraw', alpha=0.8)

plt.xlabel('Tempo (ms)', fontsize=12)
plt.ylabel('Corrente (A)', fontsize=12)
plt.title('Comparação: Modelo criado x ATPDraw', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)
plt.xlim([0, tmax * 1000])

plt.show()# Exercício de análise de redes no domínio do tempo em que é simulado um modelo de transformador

import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import Tk
import os

# dados do ATPDraw foram exportados em pl4 e convertidos para csv

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
        return None, None

dt = 1e-6  # passo de tempo
tmax = 0.2  # tempo máximo
t = np.arange(0, tmax + dt, dt)
N = len(t)

E = 220 * np.sqrt(2)  # tensão da fonte
f = 60  # frequência
theta = 0  # ângulo inicial
vs = E * np.cos(2 * np.pi * f * t + theta * np.pi / 180)

# PARÂMETROS DO TRANSFORMADOR
R1 = 1
L1 = 0.3e-3
R2 = 0.3
L2 = 0.1e-3
RM = 5e3
n = 2
LM1 = 10  # região linear
LM2 = 47.6e-3  # saturado
lb0 = 1
C = 10e-6

RL1 = 2 * L1 / dt
RL2 = 2 * L2 / dt
RC = dt / (2 * C)

x = np.zeros(12)
lb = 0
v4_ant = 0
IL1 = 0
IL2 = 0
ILM = 0
IC = 0
RLM = 2 * LM1 / dt

is_current = np.zeros(N)  # Corrente da Fonte

for m in range(N):
    tempo = t[m]


    if abs(lb) <= lb0:
        LM = LM1
    else:
        LM = LM2

    RLM = 2 * LM / dt

    if tempo < 0.01:
        # CASO 1: s1 aberta, s2 fechada
        A = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0],
            [0, 1/R1, -1/R1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, -1/R1, (1/R1 + 1/RL1), -1/RL1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, -1/RL1, (1/RL1 + 1/RM + 1/RLM), 0, 0, 0, 0, 0, 0, 0, -1/n],
            [0, 0, 0, 0, 1/R2, -1/R2, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, -1/R2, (1/R2 + 1/RL2), -1/RL2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -1/RL2, 1/RL2, 0, 0, 0, -1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1/RC, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = vs
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # isw1 = 0 (chave 1 aberta)
            [0, 0, 0, 1, -n, 0, 0, 0, 0, 0, 0, 0],  # v4 - n*v5 = 0
            [0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0]   # v7 = v8 (chave 2 fechada)
        ])

    elif tempo >= 0.01 and tempo < 0.05:
        # CASO 2: s1 fechada, s2 fechada
        A = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0],
            [0, 1/R1, -1/R1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, -1/R1, (1/R1 + 1/RL1), -1/RL1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, -1/RL1, (1/RL1 + 1/RM + 1/RLM), 0, 0, 0, 0, 0, 0, 0, -1/n],
            [0, 0, 0, 0, 1/R2, -1/R2, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, -1/R2, (1/R2 + 1/RL2), -1/RL2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -1/RL2, 1/RL2, 0, 0, 0, -1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1/RC, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = vs
            [1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = v2 (chave 1 fechada)
            [0, 0, 0, 1, -n, 0, 0, 0, 0, 0, 0, 0],  # v4 - n*v5 = 0
            [0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0]   # v7 = v8 (chave 2 fechada)
        ])

    else:
        # CASO 3: s1 fechada, s2 aberta
        A = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0],
            [0, 1/R1, -1/R1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, -1/R1, (1/R1 + 1/RL1), -1/RL1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, -1/RL1, (1/RL1 + 1/RM + 1/RLM), 0, 0, 0, 0, 0, 0, 0, -1/n],
            [0, 0, 0, 0, 1/R2, -1/R2, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, -1/R2, (1/R2 + 1/RL2), -1/RL2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -1/RL2, 1/RL2, 0, 0, 0, -1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1/RC, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = vs
            [1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # v1 = v2 (chave 1 fechada)
            [0, 0, 0, 1, -n, 0, 0, 0, 0, 0, 0, 0],  # v4 - n*v5 = 0
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]   # isw2 = 0 (chave 2 aberta)
        ])

    # Vetor b corrigido - a ordem deve corresponder às equações
    b = np.array([
        0,           # nó 0
        0,           # nó 1
        -IL1,        # nó 2 - corrente histórica do indutor L1
        IL1 - ILM,   # nó 3
        0,           # nó 4
        -IL2,        # nó 5
        IL2,         # nó 6
        -IC,         # nó 7
        vs[m],       # nó 8 (fonte)
        0,           # equação da chave 1
        0,           # equação do transformador
        0            # equação da chave 2
    ])

    try:
        x = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        print(f"Erro: Matriz singular no tempo {tempo:.6f}s")
        x = np.linalg.lstsq(A, b, rcond=None)[0]

    # Extrair variáveis na ordem correta
    v1, v2, v3, v4, v5, v6, v7, v8, i1, i2, isw1, isw2 = x
    is_current[m] = -i1  # Corrente da fonte

    # Atualização das variáveis históricas
    lb = lb + (v4 + v4_ant) * dt / 2
    v4_ant = v4
    IL1 = 2 * (v3 - v4) / RL1 + IL1
    IL2 = 2 * (v6 - v7) / RL2 + IL2
    ILM = 2 * v4 / RLM + ILM
    IC = -2 * v8 / RC - IC

# Converter de segundos para milissegundos
t_ms = t * 1000

# Carregar CSV
dados_csv = carregar_csv()

# Criar gráfico
plt.figure(figsize=(12, 6))

# Plotar simulação
plt.plot(t_ms, is_current, 'b-', linewidth=1.5, label='Modelo Proposto')

# Plotar dados do CSV se disponível
if dados_csv[0] is not None:
    tempo_csv, corrente_csv = dados_csv
    plt.plot(tempo_csv, corrente_csv, 'r--', linewidth=1.5,
             label='Resultado ATPDraw', alpha=0.8)

plt.xlabel('Tempo (ms)', fontsize=12)
plt.ylabel('Corrente (A)', fontsize=12)
plt.title('Comparação: Modelo criado x ATPDraw', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)
plt.xlim([0, tmax * 1000])

plt.show()

