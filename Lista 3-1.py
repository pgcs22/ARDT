# Exercício de análise de redes no domínio do tempo em que são simulados alguns circuitos RLC utilizando
# método MNA


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
R1 = 1  # [Ohms]
R2 = R3 = R4 = 10  # [Ohms]
L = 50E-3  # [H]
C = 50E-9  # [F]
dt = 1e-6  # [s]
tmax = 0.8  # [s]
N = int(tmax / dt) + 1

# Cálculo de Resistências equivalentes (método de integração trapezoidal)
Rl = (2 * L) / dt  # [Ohms] - resistência equivalente do indutor
Rc = dt / (2 * C)  # [Ohms] - resistência equivalente do capacitor


# As condições iniciais são zero (circuito inicialmente desenergizado)
Il1 = Il2 = Il3 = 0  # corrente histórica inicial no indutor do circuito 1
Ic1 = Ic2 = Ic3 = 0  # corrente histórica inicial no capacitor do circuito 1


# inicialização da variável tempo
t = np.linspace(0, tmax, N)

# Matrizes dos circuitos
G1 = np.array([
    [(1 / R1), (-1 / R1), 1],
    [(-1 / R1), (1 / R1 + 1 / Rl + 1 / Rc + 1 / R2), 0],
    [1, 0, 0]
])

G2 = np.array([
    [(1 / R1), (-1 / R1), 0, 0, 1],
    [(-1 / R1), (1 / R1 + 1 / R2 + 1 / R3), -1 / R2, -1 / R3, 0],
    [0, -1 / R2, (1 / R2 + 1 / Rl), 0, 0],
    [0, -1 / R3, 0, (1 / R3 + 1 / Rc), 0],
    [1, 0, 0, 0, 0]
])

G3 = np.array([
    [(1 / R1), (-1 / R1), 0, 0, 1],
    [(-1 / R1), (1 / R1 + 1 / R2 + 1 / R3), -1 / R2, -1 / R3, 0],
    [0, -1 / R2, (1 / R2 + 1 / Rl), 0, 0],
    [0, -1 / R3, 0, (1 / R3 + 1 / Rc + 1/R4), 0],
    [1, 0, 0, 0, 0]
])

I_array = np.zeros(N)

I_array2 = np.zeros(N)

I_array3 = np.zeros(N)


for n in range(N):
    # Degrau unitário: 0 para t < 0, 100 para t >= 0
    # Considerando amplitude de 100V como no código original
    if t[n] >= 0:
        vs = 1  # Degrau unitário de amplitude 100V
    else:
        vs = 0

    # Vetor de variáveis conhecidas para o circuito 1
    # [correntes conhecidas, tensões conhecidas]
    b1 = np.array([0, -Il1 - Ic1, vs])

    # Vetor de variáveis conhecidas para o circuito 2
    b2 = np.array([0, 0, -Il2, -Ic2, vs])

    # Vetor de variáveis conhecidas para o circuito 3
    b3 = np.array([0, 0, -Il3, -Ic3, vs])

    # Resolução dos sistemas matriciais
    x1 = np.linalg.solve(G1, b1)
    x2 = np.linalg.solve(G2, b2)
    x3 = np.linalg.solve(G3, b3)

    # Extração das incógnitas
    # Circuito 1: Va1 (tensão no nó a), Vb1, Is1 (corrente da fonte)
    Va1, Vb1, Is1 = x1

    # Circuito 2: Va2, Vb2, Vc2 (tensão no indutor), Vd2 (tensão no capacitor), Is2
    Va2, Vb2, Vc2, Vd2, Is2 = x2

    # Circuito 3: Va3, Vb3, Vc3 (tensão no indutor), Vd3 (tensão no capacitor), Is3
    Va3, Vb3, Vc3, Vd3, Is3 = x3

    # Armazenamento dos resultados
    I_array[n] = -Is1  # Corrente da fonte (negativo por convenção)

    I_array2[n] = -Is2  # Corrente da fonte do circuito 2

    I_array3[n] = -Is3  # Corrente da fonte do circuito 3


    # Atualização das correntes históricas dos elementos armazenadores
    # Método de integração trapezoidal (equações de diferenças)
    Il1 = 2 * Vb1 / Rl + Il1  # Corrente no indutor
    Ic1 = -2 * Vb1 / Rc - Ic1  # Corrente no capacitor
    Il2 = 2 * Vc2 / Rl + Il2  # Corrente no indutor
    Ic2 = -2 * Vd2 / Rc - Ic2  # Corrente no capacitor
    Il3 = 2 * Vc3 / Rl + Il3  # Corrente no indutor
    Ic3 = -2 * Vd3 / Rc - Ic3  # Corrente no capacitor


# Converter de segundos para milissegundos
t_ms = t * 1000

dados_csv1 = carregar_csv()

# Criar gráfico para o Circuito 1
plt.figure(figsize=(12, 6))

if dados_csv1:
    tempo_csv1, corrente_csv1 = dados_csv1
    plt.plot(tempo_csv1, corrente_csv1, 'r--', linewidth=3,
             label='Resultado ATPDraw', alpha=0.8)

# Plotar simulação
plt.plot(t_ms, I_array, 'b-', linewidth=1.5, label='Resposta ao Degrau')
plt.xlabel('Tempo (ms)', fontsize=12)
plt.ylabel('Corrente (A)', fontsize=12)
plt.title('Corrente - Circuito 1 (Resposta ao Degrau de 1V)', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)
plt.xlim([0, tmax * 1000])

plt.show()

dados_csv2 = carregar_csv()

# Criar gráfico para o Circuito 2
plt.figure(figsize=(12, 6))

if dados_csv2:
    tempo_csv2, corrente_csv2 = dados_csv2
    plt.plot(tempo_csv2, corrente_csv2, 'r--', linewidth=3,
             label='Resultado ATPDraw', alpha=0.8)

# Plotar simulação
plt.plot(t_ms, I_array2, 'b-', linewidth=1.5, label='Resposta ao Degrau')
plt.xlabel('Tempo (ms)', fontsize=12)
plt.ylabel('Corrente (A)', fontsize=12)
plt.title('Corrente - Circuito 2 (Resposta ao Degrau de 1V)', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)
plt.xlim([0, tmax * 1000])


plt.show()


dados_csv3 = carregar_csv()

# Criar gráfico para o Circuito 2
plt.figure(figsize=(12, 6))

if dados_csv3:
    tempo_csv3, corrente_csv3 = dados_csv3
    plt.plot(tempo_csv3, corrente_csv3, 'r--', linewidth=3,
             label='Resultado ATPDraw', alpha=0.8)

# Plotar simulação
plt.plot(t_ms, I_array3, 'b-', linewidth=1.5, label='Resposta ao Degrau')
plt.xlabel('Tempo (ms)', fontsize=12)
plt.ylabel('Corrente (A)', fontsize=12)
plt.title('Corrente - Circuito 3 (Resposta ao Degrau de 1V)', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)
plt.xlim([0, tmax * 1000])


plt.show()