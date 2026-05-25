import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import Tk
import os

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

# Parâmetros de Entrada
dt = 1e-6  # Passo de simulação (s)
tmax = 0.8  # Tempo máximo (s)
E = 1  # Tensão aplicada (V)
R1 = 1  # Resistência (Ohms)
R2 = R3 = R4 = 10  # Resistência (Ohms)
L = 50e-3  # Indutância (H)
C = 50e-9  # Capacitância (F)

# Matrizes de estado do Circuito 1:
A1 = np.array([[-(R1+R2)/(R1*R2*C), -1/C],
              [1/L, 0]])
B1 = np.array([[1/(R1*C)],
              [0]])
C_matrix1 = np.array([[-1/R1, 0]])
D1 = 1/R1


# matrizes de estados do circuito 2
A2 = np.array([[-1/((R1+R3)*C), -R1/((R1+R3)*C)],
              [R1/((R1+R3)*L), ((-R1*R3-R2*R3-R1*R2)/((R1+R3)*L))]])

B2 = np.array([[1/((R1+R3)*C)],
              [R3/((R1+R3)*L)]])

C_matrix2 = np.array([[-1/(R1+R3), R3/(R1+R3)]])
D2 = 1/(R1+R3)

# Matrizes de estados do Circuito 3
A3 = np.array([[(-R1-R3-R4)/((C*R4)*(R1+R3)), -R1/(C*(R1+R3))],
              [R1/(L*(R1+R3)), ((-R1*R3-R2*R3-R1*R2)/(L*(R1+R3)))]])
B3 = np.array([[1/((R1+R3)*C)],
              [R3/((R1+R3)*L)]])
C_matrix3 = np.array([[-1/(R1+R3), R3/(R1+R3)]])
D3 = 1/(R1+R3)


I = np.eye(2)

inv_term1 = np.linalg.inv(I - A1 * dt / 2)
inv_term2 = np.linalg.inv(I - A2 * dt / 2)
inv_term3 = np.linalg.inv(I - A3 * dt / 2)

# Integração trapezoidal no circuito 1
alfa1 = inv_term1 @ (I + A1 * dt / 2)
lamb1 = inv_term1 * (dt / 2)  # ou (dt/2) * inv_term
mu1 = lamb1

# Integração trapezoidal no circuito 2
alfa2 = inv_term2 @ (I + A2 * dt / 2)
lamb2 = inv_term2 * (dt / 2)  # ou (dt/2) * inv_term
mu2 = lamb2

# Integração trapezoidal no circuito 3
alfa3 = inv_term3 @ (I + A3 * dt / 2)
lamb3 = inv_term3 * (dt / 2)  # ou (dt/2) * inv_term
mu3 = lamb3


# Matrizes do sistema discreto circuito 1
AA1 = alfa1
BB1 = B1
CC1 = C_matrix1 @ (alfa1 @ lamb1 + mu1)
DD1 = (C_matrix1 @ lamb1 @ B1) + D1

# Matrizes do sistema discreto circuito 2
AA2 = alfa2
BB2 = B2
CC2 = C_matrix2 @ (alfa2 @ lamb2 + mu2)
DD2 = (C_matrix2 @ lamb2 @ B2) + D2

# Matrizes do sistema discreto circuito 3
AA3 = alfa3
BB3 = B3
CC3 = C_matrix3 @ (alfa3 @ lamb3 + mu3)
DD3 = (C_matrix3 @ lamb3 @ B3) + D3


# Vetor de tempo
N = round(tmax / dt) + 1
t = np.linspace(0, tmax, N)


u = np.zeros(N)
u[1:] = E  # Degrau a partir de t=dt

# Inicialização
x1 = np.zeros((2, 1))  # Estados iniciais: [tensão no capacitor; corrente no indutor]
y1 = np.zeros(N)  # Saída (corrente)
x2 = np.zeros((2, 1))  # Estados iniciais: [tensão no capacitor; corrente no indutor]
y2 = np.zeros(N)  # Saída (corrente)
x3 = np.zeros((2, 1))  # Estados iniciais: [tensão no capacitor; corrente no indutor]
y3 = np.zeros(N)  # Saída (corrente)

# Simulação do sistema discreto
for n in range(N):
    # Calcula saída atual
    y1[n] = (CC1 @ x1 + DD1 * u[n]).item()
    y2[n] = (CC2 @ x2 + DD2 * u[n]).item()
    y3[n] = (CC3 @ x3 + DD3 * u[n]).item()
    # Atualiza estado para próximo passo
    x1 = AA1 @ x1 + BB1 * u[n]
    x2 = AA2 @ x2 + BB2 * u[n]
    x3 = AA3 @ x3 + BB3 * u[n]


dados_csv1 = carregar_csv()

# Criar gráfico para o Circuito 1
plt.figure(figsize=(12, 6))

if dados_csv1:
    tempo_csv1, corrente_csv1 = dados_csv1
    plt.plot(tempo_csv1, corrente_csv1, 'r--', linewidth=3,
             label='Resultado ATPDraw', alpha=0.8)

plt.plot(t * 1000, y1)  # Convertendo para ms
plt.xlabel('Tempo (ms)')
plt.ylabel('Corrente (A)')
plt.title('Resposta do Circuito 1')
plt.grid(True, alpha=0.3)
plt.show()

dados_csv2 = carregar_csv()

# Criar gráfico para o Circuito 2
plt.figure(figsize=(12, 6))

if dados_csv2:
    tempo_csv2, corrente_csv2 = dados_csv2
    plt.plot(tempo_csv2, corrente_csv2, 'r--', linewidth=3,
             label='Resultado ATPDraw', alpha=0.8)

plt.plot(t * 1000, y2)  # Convertendo para ms
plt.xlabel('Tempo (ms)')
plt.ylabel('Corrente (A)')
plt.title('Resposta do Circuito 2')
plt.grid(True, alpha=0.3)
plt.show()

dados_csv3 = carregar_csv()

# Criar gráfico para o Circuito 3
plt.figure(figsize=(12, 6))

if dados_csv3:
    tempo_csv3, corrente_csv3 = dados_csv3
    plt.plot(tempo_csv3, corrente_csv3, 'r--', linewidth=3,
             label='Resultado ATPDraw', alpha=0.8)

plt.plot(t * 1000, y3)  # Convertendo para ms
plt.xlabel('Tempo (ms)')
plt.ylabel('Corrente (A)')
plt.title('Resposta do Circuito 3')
plt.grid(True, alpha=0.3)
plt.show()
