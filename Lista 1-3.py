import numpy as np
import matplotlib.pyplot as plt

tmax = 150E-6 # [s]
dt = 0.1E-6 # [s]
N = round(tmax/dt)+1

# inicialização das variáveis
t = np.linspace(0, tmax, N)
vc = np.zeros(N)

# Simulação
for n in range(1, N):
    vc[n] = 10 + 2*4.99*np.exp(-5E4 * t[n]) * np.cos(1E6 * t[n] + 3.09)

# desenho dos gráficos
plt.figure(figsize=(10, 6))
plt.plot(t, vc, 'b-', linewidth=1.5)
plt.xlabel('Tempo (s)', fontsize=12)
plt.ylabel('Tensão no capacitor (V)', fontsize=12)
plt.title('Tensão no capacitor', fontsize=14)
plt.grid(alpha=0.3)
plt.xlim(0, tmax)
plt.show()