import numpy as np
import matplotlib.pyplot as plt
from scipy.special import iv as besseli
from tkinter import filedialog
from tkinter import Tk
import os
from scipy import signal

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

# Constantes
mu0 = 4 * np.pi * 1e-7
eps0 = 8.85418782e-12


H = 10
r = 10e-3
Rs = 50
Rld = 500
sigma = 5.8e7
rho = 500
comprimento = 20E3
dt = 1e-6
tmax = 0.002  # [s]
N = int(tmax / dt) + 1
largura_pulso = 0.5E-3  # 0.5 ms


f = 60
w = 2 * np.pi * f

Lext = mu0 * np.log(2 * H / r) / (2 * np.pi)
Zext = 1j * w * Lext

arg = np.sqrt(1j * w * mu0 * sigma) * r
Zint = (1 / (2 * np.pi * r)) * np.sqrt(1j * w * mu0 / sigma) * besseli(0, arg) / besseli(1, arg)

p = np.sqrt(rho/ (1j * w * mu0))
Zsolo= 1j * f * mu0 * np.log((H + p) / H)

# Impedância total
Z = (Zext + Zint + Zsolo)
R = Z.real * comprimento
L = (Z.imag)/(2*np.pi*f) * comprimento
C = eps0 * mu0 / Lext * comprimento
C1=C2 = C/2

Rl = (2 * L) / dt  # [Ohms] - resistência equivalente do indutor
Rc1 = Rc2 = dt / (2 * C1)  # [Ohms] - resistência equivalente do capacitor


Il = Ic1 = Ic2 = 0

G = np.array([
    [(1 / Rs), (-1 / Rs), 0, 0, 1],
    [(-1 / Rs), (1 / Rs + 1 / Rc1 + 1 / R), (-1 / R), 0, 0],
    [0, (-1 / R), (1 / R + 1 / Rl), (-1/Rl), 0],
    [0, 0, -(1/Rl), (1 / Rl + 1 / Rc2 + 1 / Rld), 0],
    [1, 0, 0, 0, 0]
])

V_array = np.zeros(N)

t = np.linspace(0, tmax, N)

# Gera onda quadrada periódica
periodo = tmax
frequencia = 1 / periodo
duty = largura_pulso / periodo

onda_quadrada = signal.square(2 * np.pi * frequencia * t, duty=duty)

# Converte de [-1, 1] para [0, 1] e ajusta amplitude
Vs = (onda_quadrada + 1) / 2

for n in range(N):

    b = np.array([0, -Ic1, -Il, Il-Ic2, Vs[n]])  # CORREÇÃO: usar Vs[n]

    # Resolução dos sistemas matriciais
    x = np.linalg.solve(G, b)


    # Circuito 1: Va1 (tensão no nó a), Vb1, Is1 (corrente da fonte)
    Va, Vb, Vc, Vd, Is = x

    # Armazenamento dos resultados
    V_array[n] = Vd  # Tensão na carga


    # Atualização das correntes históricas dos elementos armazenadores
    # Método de integração trapezoidal (equações de diferenças)
    Il = 2 * (Vc-Vd) / Rl + Il  # Corrente no indutor
    Ic1 = -2 * Vb / Rc1 - Ic1  # Corrente no capacitor
    Ic2 = -2 * Vd / Rc2 - Ic2  # Corrente no capacitor


# Converter de segundos para milissegundos
t_ms = t * 1000


dados_csv = carregar_csv()

plt.figure(figsize=(10, 4))
if dados_csv:
    tempo_csv, tensao_csv = dados_csv
    plt.plot(tempo_csv, tensao_csv, 'g.', linewidth=2,
             label='Resultado ATPDraw', alpha=0.8)


plt.plot(t * 1000, Vs, 'r--', label='Sinal de entrada (pulso)', linewidth=2, alpha=0.7)
plt.plot(t * 1000, V_array, 'b-', linewidth=1.5, label='Tensão na carga (Vd)', alpha=0.7)
plt.xlabel('Tempo (ms)')
plt.ylabel('Tensão (V)')
plt.title('Resposta do circuito ao pulso de 0.5ms')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim([0, 2])  # Mostra apenas os primeiros 2ms
plt.ylim([-0.2, 1.2])
plt.show()