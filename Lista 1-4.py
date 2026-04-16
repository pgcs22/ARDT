import numpy as np
import matplotlib.pyplot as plt

# Definição das variáveis de entrada
E = 10 # [V]
dt = 0.1E-6 # [s]
L = 1E-3 # [H]
R = 100 # [Ohms]
C = 1E-9 # [F]
tmax = 150E-6 # [s]

# Cáculo das cosntantes
Rl = (2*L)/dt
Rc = dt/(C*2)
N = round(tmax/dt)+1

# inicialização das variáveis
t = np.linspace(0, tmax, N)
vs = np.zeros(N)
v2 = np.zeros(N)
vc = np.zeros(N)
v3 = np.zeros(N)
i = np.zeros(N)
Il = 0
Ic = 0
vs[2:N]=E

# Simulação
for n in range(1, N):
    v2[n] = 0.995*vs[n]-99.255*Il-0.24811*Ic
    v3[n] = 0.0025*vs[n]+49.6278*Il-49.8759*Ic
    vc[n] = 10 + 2 * 4.99 * np.exp(-5E4 * t[n]) * np.cos(1E6 * t[n] + 3.09)
    Il = 10E-5*(v2[n]-v3[n])+Il
    Ic = -0.04*v3[n]-Ic
    i[n] = (vs[n]-v2[n])/R

# desenho dos gráficos

plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.plot(t, i, 'b-', linewidth=1.5, label='Corrente')
plt.xlabel('Tempo (s)', fontsize=12)
plt.ylabel('Corrente (A)', fontsize=12)
plt.title('Corrente', fontsize=14)
plt.grid(alpha=0.3)
plt.xlim(0, tmax)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(t, v3, 'b-', linewidth=1.5, label='Tensão no capacitor - Método trapezoidal')
plt.plot(t, vc, 'r--', linewidth=1.5, label='Tensão no capacitor - Método Analítico')
plt.xlabel('Tempo (s)', fontsize=12)
plt.ylabel('Tensão (V)', fontsize=12)
plt.title('Tensões no circuito', fontsize=14)
plt.grid(alpha=0.3)
plt.xlim(0, tmax)
plt.ylim(0, 20)
plt.legend()

plt.tight_layout()
plt.show()