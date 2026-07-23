import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
import traceback

def carregar_csv():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo CSV",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )

    root.destroy()

    if not arquivo:
        return None, None, None, None

    codificacoes = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-16le', 'utf-16be']

    for encoding in codificacoes:
        try:
            with open(arquivo, 'r', encoding=encoding) as f:
                linhas = f.readlines()

            teste_linha = linhas[3] if len(linhas) > 3 else ""
            if any(c.isdigit() for c in teste_linha):
                break
        except Exception as e:
            continue
    else:
        with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            linhas = f.readlines()

    try:
        # Pular cabeçalho
        inicio_dados = 0
        for i, linha in enumerate(linhas):
            linha_limpa = linha.strip()
            if linha_limpa and not linha_limpa.startswith('"') and not linha_limpa.startswith('#'):
                partes = linha_limpa.split(',')
                try:
                    float(partes[0].strip())
                    inicio_dados = i
                    break
                except:
                    continue

        dados_linhas = linhas[inicio_dados:]

        tempo_csv = []
        tensao1_csv = []
        tensao2_csv = []
        tensao3_csv = []

        for i, linha in enumerate(dados_linhas):
            linha = linha.strip()
            if linha:
                # Remover aspas se presentes
                linha = linha.replace('"', '').replace("'", "")
                partes = linha.split(',')

                # Tentar diferentes separadores decimais
                if len(partes) >= 4:
                    try:
                        # Tentar com ponto decimal
                        tempo = float(partes[0].strip())
                        tensao1 = float(partes[1].strip())
                        tensao2 = float(partes[2].strip())
                        tensao3 = float(partes[3].strip())
                    except ValueError:
                        try:
                            # Tentar com vírgula decimal (substituir , por .)
                            tempo = float(partes[0].strip().replace(',', '.'))
                            tensao1 = float(partes[1].strip().replace(',', '.'))
                            tensao2 = float(partes[2].strip().replace(',', '.'))
                            tensao3 = float(partes[3].strip().replace(',', '.'))
                        except ValueError:
                            continue

                    tempo_csv.append(tempo)
                    tensao1_csv.append(tensao1)
                    tensao2_csv.append(tensao2)
                    tensao3_csv.append(tensao3)

        if len(tempo_csv) == 0:
            return None, None, None, None

        # Converter para arrays numpy
        tempo_csv = np.array(tempo_csv)

        # Verificar se o tempo está em segundos ou milissegundos
        if np.max(tempo_csv) < 10:  # Provavelmente em segundos
            tempo_csv = tempo_csv * 1000  # Converter para ms

        tensao1_csv = np.array(tensao1_csv)
        tensao2_csv = np.array(tensao2_csv)
        tensao3_csv = np.array(tensao3_csv)

        return tempo_csv, tensao1_csv, tensao2_csv, tensao3_csv

    except Exception as e:
        traceback.print_exc()
        return None, None, None, None

# Parâmetros da simulação
dt = 0.25e-6
tmax = 100e-6
E = 1000
R1 = 400
Zs1 = 400
l1 = 600
v1 = 3e8
Zs2 = 50
v2 = 1.5e8
l2 = 300

tau = l1 / v1
deff = round(tau / dt)
N = round(tmax / dt) + 1
t = np.linspace(0, tmax, N)

is_ = E * np.ones(N) / R1

G = np.array([
    [1/R1 + 1/Zs1, 0, 0],
    [0, 1/Zs1 + 1/Zs2, 0],
    [0, 0, 1/Zs2]
])

vk = np.zeros(N)
vm = np.zeros(N)
vx = np.zeros(N)
Ik1 = np.zeros(N)
Im1 = np.zeros(N)
Ik2 = np.zeros(N)
Im2 = np.zeros(N)

# Laço temporal
for n in range(N):
    if n < deff:
        b = np.array([is_[n], 0, 0])
        x = np.linalg.solve(G, b)
        vk[n] = x[0]
        vm[n] = x[1]
        vx[n] = x[2]
        Ik1[n] = (2 / Zs1) * vm[n]
        Im1[n] = (2 / Zs1) * vk[n]
        Ik2[n] = (2 / Zs2) * vx[n]
        Im2[n] = (2 / Zs2) * vm[n]
    else:
        b = np.array([
            is_[n] + Ik1[n - deff],
            Im1[n - deff] + Ik2[n - deff],
            Im2[n - deff]
        ])
        x = np.linalg.solve(G, b)
        vk[n] = x[0]
        vm[n] = x[1]
        vx[n] = x[2]
        Ik1[n] = (2 / Zs1) * vm[n] - Im1[n - deff]
        Im1[n] = (2 / Zs1) * vk[n] - Ik1[n - deff]
        Ik2[n] = (2 / Zs2) * vx[n] - Im2[n - deff]
        Im2[n] = (2 / Zs2) * vm[n] - Ik2[n - deff]

# Carregar dados do CSV
print("Selecione o arquivo CSV com os dados experimentais...")
tempo_csv, tensao1_csv, tensao2_csv, tensao3_csv = carregar_csv()

# Plot
t_us = t * 1e6

plt.figure(figsize=(12, 8))

# Plot da simulação
plt.plot(t_us, vk, 'b-', linewidth=1.5, label='Nó k - Calculado')
plt.plot(t_us, vm, 'r-', linewidth=1.5, label='Nó m - Simulação')
plt.plot(t_us, vx, 'g-', linewidth=1.5, label='Nó x - Calculado')

# Plot dos dados do CSV (se carregados com sucesso)
if tempo_csv is not None and tensao1_csv is not None:
    plt.plot(tempo_csv, tensao1_csv, 'b--', linewidth=1, alpha=0.7, label='Nó k - ATPWDraw')
    plt.plot(tempo_csv, tensao2_csv, 'r--', linewidth=1, alpha=0.7, label='Nó m - ATPWDraw')
    plt.plot(tempo_csv, tensao3_csv, 'g--', linewidth=1, alpha=0.7, label='Nó x - ATPWDraw')
    print("Dados do CSV carregados com sucesso!")
    print(f"Tamanho dos dados: {len(tempo_csv)} pontos")
else:
    print("Nenhum dado CSV carregado ou erro na leitura.")

plt.xlabel('tempo [μs]')
plt.ylabel('tensão [V]')
plt.legend(loc='lower right')
plt.grid(True, alpha=0.3)
plt.xlim([0, 100])
plt.ylim([0, 1100])
plt.title('Comparação Geral - Todos os Nós')
plt.tight_layout()
plt.show()