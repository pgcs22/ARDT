import numpy as np
import matplotlib.pyplot as plt

# Definição das variáveis de entrada
E = 10 # [V]
dt = 0.005E-6 # [s]
L = 1E-3 # [H]
R = 100 # [Ohms]
C = 1E-9 # [F]
tmax = 150E-6 # [s]

# Cáculo das cosntantes
Rl = (L)/dt
Rc = dt/(C)
N = round(tmax/dt)+1

# inicialização das variáveis
t = np.linspace(0, tmax, N)
vs = np.zeros(N)
v2 = np.zeros(N)
vc = np.zeros(N)
v3 = np.zeros(N)
vc = np.zeros(N)
va = np.zeros(N)
i = np.zeros(N)
Il = 0
Ic = 0
vs[2:N] = E

# Cálculo dos termos da matriz A
termo_11 = (1/R + 1/Rl)  # (1/100 + 1/20000)
termo_12 = -1/Rl               # -1/20000
termo_21 = -1/Rl               # -1/20000
termo_22 = (1/Rc + 1/Rl) # (1/50 + 1/20000)

# Construindo a matriz A
Gbb = np.array([
    [termo_11, termo_12],
    [termo_21, termo_22]
])
Gba = np.array([[-1/R], [0]])

# Calculando a inversa da matriz Gbb
Gbb_inv = np.linalg.inv(Gbb)

# Simulação
for n in range(1, N):
    IB = [-Il, (Il - Ic)]
    VB = Gbb_inv @ (IB - (Gba @ np.array([vs[n]])).flatten())  # CORRIGIDO: usando a inversa
    v2[n] = VB[0]  # Tensão no nó 2
    v3[n] = VB[1]  # Tensão no nó 3 (capacitor)
    vc[n] = v3[n]  # Tensão no capacitor
    Il = (v2[n] - v3[n]) / Rl + Il  # CORRIGIDO: atualização da corrente no indutor
    Ic = -v3[n] / Rc  # CORRIGIDO: corrente no capacitor
    i[n] = (vs[n] - v2[n]) / R  # CORRIGIDO: corrente no resistor
    va[n] = 10 + 2 * 4.99 * np.exp(-5E4 * t[n]) * np.cos(1E6 * t[n] + 3.09)

# desenho dos gráficos

plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.plot(t, i, 'b-', linewidth=1.5, label='Corrente no indutor')
plt.xlabel('Tempo (s)', fontsize=12)
plt.ylabel('Corrente (A)', fontsize=12)
plt.title('Corrente no indutor', fontsize=14)
plt.grid(alpha=0.3)
plt.xlim(0, tmax)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(t, v3, 'b-', linewidth=1.5, label='Tensão no capacitor - Método Euller')
plt.plot(t, va, 'r--', linewidth=1.5, label='Tensão no capacitor - Método analítico')
plt.xlabel('Tempo (s)', fontsize=12)
plt.ylabel('Tensão (V)', fontsize=12)
plt.title('Tensões no circuito', fontsize=14)
plt.grid(alpha=0.3)
plt.xlim(0, tmax)
plt.ylim(0, 20)
plt.legend()

plt.tight_layout()
plt.show()