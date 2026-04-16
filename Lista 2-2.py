# Exercício de análise de redes no domínio do tempo em que é simulado a abertura de um disjuntor
# à vácuo utilizando o método MNA e integração trapezoidal

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
L1 = 5E-3 #[H]
R2 = 5 #[Ohms]
L2 = 50E-3 #[H]
C = 50E-9 #[F]
dt = 1e-6 #[s]
tmax = 0.08 #[s]
N = int(tmax / dt) + 1

# Cálculo de Resistências equivalentes
Rl1 = (2 * L1) / dt#[Ohms]
Rl2 = (2 * L2) / dt#[Ohms]
Rc = dt / (2*C)#[Ohms]

# Cálculo das impedâncias do circuito
zl1 = 1j * 377 * L1  # Impedância do L1
zl2 = 1j * 377 * L2  # Impedância do L2
zc = 1 / (1j * 377 * C)  # Impedância do C


# Impedancia equivalente vista pela fonte
Z1 = R2 + zl2  # R2 serie com L2
Zdisj = (Z1 * zc) / (Z1 + zc)
Z_total = R1 + zl1 + Zdisj  # impedancia vista pela fonte


is_t = 100 / Z_total

# Corrente no indutor L2
i_t = is_t * zc / (Z1 + zc)

# Corrente no capacitor
ic_t = is_t - i_t

# Tensoes nos elementos armazenadores
vl1 = zl1 * is_t
vl2 = zl2 * i_t
vc = zc * ic_t

# Corrente inicial nas fontes de corrente dos indutores e do capacitor

Il1 = (abs(is_t) * np.cos(377 * (-dt) + np.angle(is_t)) +
         (abs(vl1) / Rl1) * np.cos(377 * (-dt) + np.angle(vl1)))
Il2= (abs(i_t) * np.cos(377 * (-dt) + np.angle(i_t)) +
         (abs(vl2) / Rl2) * np.cos(377 * (-dt) + np.angle(vl2)))
Ic = (-abs(ic_t) * np.cos(377 * (-dt) + np.angle(ic_t)) -
        (abs(vc) / Rc) * np.cos(377 * (-dt) + np.angle(vc)))

# inicialização da variável tempo
t = np.linspace(0, tmax, N)


# Termos da matriz
termo_11, termo_12, termo_13, termo_14, termo_15, termo_16, termo_17 = (1 / R1), (-1 / R1), 0, 0, 0, 0, 1
termo_21, termo_22, termo_23, termo_24, termo_25, termo_26, termo_27 =\
    (-1 / R1), (1 / R1 + 1 / Rl1), (-1 / Rl1), 0, 0, 0, 0
termo_31, termo_32, termo_33, termo_34, termo_35, termo_36, termo_37 = 0, (-1 / Rl1), (1 / Rl1), 0, 0, 1, 0
termo_41, termo_42, termo_43, termo_44, termo_45, termo_46, termo_47 = \
    0, 0, 0, (1 / R2 + 1 / Rc), (-1 / R2), -1, 0
termo_51, termo_52, termo_53, termo_54, termo_55, termo_56, termo_57 =\
    0, 0, 0,(-1 / R2), (1 / R2 + 1 / Rl2), 0, 0
termo_61, termo_62, termo_63, termo_64, termo_65, termo_66, termo_67 = 1, 0, 0, 0, 0, 0, 0
termo_71, termo_72, termo_73, termo_74, termo_75, termo_76, termo_77 = 0, 0, 1, -1, 0, 0, 0

termo_73b, termo_74b, termo_77b = 0, 0, 1# termos que se alteram no fechamento da chave


# Matriz da chave fechada (antes da abertura do disjuntor) - 7x7
G_fechada = np.array([
    [termo_11, termo_12, termo_13, termo_14, termo_15, termo_16, termo_17],
    [termo_21, termo_22, termo_23, termo_24, termo_25, termo_26, termo_27],
    [termo_31, termo_32, termo_33, termo_34, termo_35, termo_36, termo_37],
    [termo_41, termo_42, termo_43, termo_44, termo_45, termo_46, termo_47],
    [termo_51, termo_52, termo_53, termo_54, termo_55, termo_56, termo_57],
    [termo_61, termo_62, termo_63, termo_64, termo_65, termo_66, termo_67],
    [termo_71, termo_72, termo_73, termo_74, termo_75, termo_76, termo_77]
])

# Matriz da chave aberta (abertura do disjuntor) - 7x7
G_aberta = np.array([
    [termo_11, termo_12, termo_13, termo_14, termo_15, termo_16, termo_17],
    [termo_21, termo_22, termo_23, termo_24, termo_25, termo_26, termo_27],
    [termo_31, termo_32, termo_33, termo_34, termo_35, termo_36, termo_37],
    [termo_41, termo_42, termo_43, termo_44, termo_45, termo_46, termo_47],
    [termo_51, termo_52, termo_53, termo_54, termo_55, termo_56, termo_57],
    [termo_61, termo_62, termo_63, termo_64, termo_65, termo_66, termo_67],
    [termo_71, termo_72, termo_73b, termo_74b, termo_75, termo_76, termo_77b]
])


I_array = np.zeros(N)
V_array = np.zeros(N)

for n in range(N):
    vs = 100 * np.cos(377 * t[n])
    b = np.array([0, -Il1, Il1, -Ic, -Il2, vs, 0])# matriz de variáveis conhecidas
    if (t[n] > 0.03) and (n > 0) and (abs(I_array[n - 1]) < 0.5):
        G = G_aberta
    else:
        G = G_fechada
    x = np.linalg.solve(G, b)# resolução do sistema matricial
    V1, V2, V3, V4, V5, Is, Ich = x# matriz de incógnitas
    I_array[n] = Is
    V_array[n] = V4
    Il1 = 2 * (V2 - V3) / Rl1 + Il1# atualização do valor da corrente no indutor
    Il2 = 2 * (V5) / Rl2 + Il2
    Ic = -2 * (V4) / Rc - Ic


#converter de microssegundos para milissegundos
t_ms = t * 1000

# Carregar CSV
dados_csv = carregar_csv()

# Criar gráfico
plt.figure(figsize=(12, 6))

# Plotar simulação
plt.plot(t_ms, V_array, 'b-', linewidth=1.5, label='Modelo Proposto')

# Plotar dados do CSV se disponível
if dados_csv:
    tempo_csv, corrente_csv = dados_csv
    plt.plot(tempo_csv, corrente_csv, 'r--', linewidth=1.5,
             label='Resultado ATPDraw', alpha=0.8)

plt.axvline(x=30, color='g', linestyle=':', linewidth=2, label='abertura do disjuntor')
plt.xlabel('Tempo (ms)', fontsize=12)
plt.ylabel('Tensão (V)', fontsize=12)
plt.title('Comparação: Modelo criado x ATPDraw', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)
plt.xlim([0, tmax * 1000])

plt.show()