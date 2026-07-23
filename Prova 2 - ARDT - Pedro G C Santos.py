import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from tkinter import filedialog, Tk
from tkinter import messagebox
import traceback


def carregar_csv(arquivo=None):
    """
    Carrega um arquivo CSV com 2 curvas de tensão
    Retorna: tempo, tensao1, tensao2
    """
    if arquivo is None:
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )

        root.destroy()

        if not arquivo:
            return None, None, None

    # Tentar diferentes codificações
    codificacoes = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-16le', 'utf-16be']
    linhas = None

    for encoding in codificacoes:
        try:
            with open(arquivo, 'r', encoding=encoding) as f:
                linhas = f.readlines()

            # Testar se a codificação está correta
            teste_linha = linhas[3] if len(linhas) > 3 else ""
            if any(c.isdigit() for c in teste_linha):
                break
        except Exception:
            continue

    if linhas is None:
        with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            linhas = f.readlines()

    try:
        # Encontrar início dos dados
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

        for i, linha in enumerate(dados_linhas):
            linha = linha.strip()
            if linha:
                # Remover aspas se presentes
                linha = linha.replace('"', '').replace("'", "")
                partes = linha.split(',')

                # Verificar se tem pelo menos 3 colunas (tempo + 2 tensões)
                if len(partes) >= 3:
                    try:
                        # Tentar com ponto decimal
                        tempo = float(partes[0].strip())
                        tensao1 = float(partes[1].strip())
                        tensao2 = float(partes[2].strip())
                    except ValueError:
                        try:
                            # Tentar com vírgula decimal
                            tempo = float(partes[0].strip().replace(',', '.'))
                            tensao1 = float(partes[1].strip().replace(',', '.'))
                            tensao2 = float(partes[2].strip().replace(',', '.'))
                        except ValueError:
                            continue

                    tempo_csv.append(tempo)
                    tensao1_csv.append(tensao1)
                    tensao2_csv.append(tensao2)

        if len(tempo_csv) == 0:
            return None, None, None

        # Converter para arrays numpy
        tempo_csv = np.array(tempo_csv)
        tensao1_csv = np.array(tensao1_csv)
        tensao2_csv = np.array(tensao2_csv)

        # Verificar se o tempo está em segundos ou milissegundos
        if np.max(tempo_csv) < 10:  # Provavelmente em segundos
            tempo_csv = tempo_csv * 1000  # Converter para ms

        return tempo_csv, tensao1_csv, tensao2_csv

    except Exception as e:
        traceback.print_exc()
        return None, None, None


def carregar_dois_csv():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    messagebox.showinfo("Abrir Arquivo",
                        "Selecione o PRIMEIRO arquivo CSV (2 curvas de tensão)")

    arquivo1 = filedialog.askopenfilename(
        title="Selecione o primeiro arquivo CSV",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )

    if not arquivo1:
        root.destroy()
        return None, None, None, None, None, None

    # Mensagem para o segundo arquivo
    messagebox.showinfo("Abrir Arquivo",
                        "Selecione o SEGUNDO arquivo CSV (2 curvas de tensão)")

    arquivo2 = filedialog.askopenfilename(
        title="Selecione o segundo arquivo CSV",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )

    root.destroy()

    if not arquivo2:
        return None, None, None, None, None, None

    # Carregar os arquivos
    tempo1, v1_1, v1_2 = carregar_csv(arquivo1)
    tempo2, v2_1, v2_2 = carregar_csv(arquivo2)

    return tempo1, v1_1, v1_2, tempo2, v2_1, v2_2


dt = 1e-6  # passo de tempo [s]
tmax = 0.1  # tempo máximo [s]
f = 60  # frequência [Hz]
w = 2 * np.pi * f
E = 1000  # amplitude da fonte [V]
l = 30_000  # comprimento da linha [m]
v = 3e8  # velocidade de propagação [m/s]
tau = l / v  # atraso de propagação [s]

N = int(round(tmax / dt)) + 1
deff = int(round(tau / dt))
t = np.linspace(0, tmax, N)

Zs = np.array([[500, 180],
               [180, 500]], dtype=float)

Zs_inv = np.linalg.inv(Zs)

R = 1000.0
Yr = 1 / R

Ya_load = np.array([[0, 0],
                    [0, Yr]], dtype=float)

Yb_load = np.array([[Yr, 0],
                    [0, 0]], dtype=float)

Aa = Ya_load + Zs_inv
Ab = Yb_load + Zs_inv

Ab_inv = np.linalg.inv(Ab)

Vsrc = E * np.cos(w * t)

va = np.zeros((2, N))
vb = np.zeros((2, N))

Ia_hist = np.zeros((2, N))
Ib_hist = np.zeros((2, N))

for n in range(N):
    nd = n - deff

    if nd >= 0:
        Ia_hist[:, n] = 2 * Zs_inv @ vb[:, nd] - Ib_hist[:, nd]
        Ib_hist[:, n] = 2 * Zs_inv @ va[:, nd] - Ia_hist[:, nd]

    Va1 = Vsrc[n]
    Va2 = (Ia_hist[1, n] - Aa[1, 0] * Va1) / Aa[1, 1]
    va[:, n] = [Va1, Va2]
    vb[:, n] = Ab_inv @ Ib_hist[:, n]

# ============================================
# CARREGAR DADOS DOS CSVs
# ============================================
t_ms = t * 1e3

tempo1, v1_fase1, v1_fase2, tempo2, v2_fase1, v2_fase2 = carregar_dois_csv()

fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
fig.suptitle('Prova ARDT'
             , fontsize=13, fontweight='bold')

colors = ['red', 'blue']
colors_CSV = ['green', 'yellow']
labels = ['Condutor 1', 'Condutor 2']

ax = axes[0]

for k in range(2):
    ax.plot(t_ms, va[k, :], color=colors[k], linewidth=1.4, label=labels[k])

if tempo1 is not None:
    ax.plot(tempo1, v1_fase1, color=colors_CSV[0], linewidth=1.4,
            linestyle='--', label=f'{labels[0]} (CSV)')
    ax.plot(tempo1, v1_fase2, color=colors_CSV[1], linewidth=1.4,
            linestyle='--', label=f'{labels[1]} (CSV)')

ax.set_ylabel('Tensão [V]', fontsize=11)
ax.set_title('Barra A', fontsize=11)
ax.legend(fontsize=9, loc='upper right')
ax.grid(True, linestyle='--', alpha=0.5)
ax.axhline(0, color='black', linewidth=0.5)

ax = axes[1]

for k in range(2):
    ax.plot(t_ms, vb[k, :], color=colors[k], linewidth=1.4, label=labels[k])

if tempo2 is not None:
    ax.plot(tempo2, v2_fase1, color=colors_CSV[0], linewidth=1.4,
            linestyle='--', label=f'{labels[0]} (CSV)')
    ax.plot(tempo2, v2_fase2, color=colors_CSV[1], linewidth=1.4,
            linestyle='--', label=f'{labels[1]} (CSV)')

ax.set_xlabel('Tempo [ms]', fontsize=11)
ax.set_ylabel('Tensão [V]', fontsize=11)
ax.set_title('Barra B', fontsize=11)
ax.legend(fontsize=9, loc='upper right')
ax.grid(True, linestyle='--', alpha=0.5)
ax.axhline(0, color='black', linewidth=0.5)

plt.tight_layout()
plt.show()
plt.close()