import numpy as np
import matplotlib.pyplot as plt

# Definição das variáveis de entrada
Vm = 100 # [V]
dt = 1E-6 # [s]
tmax = 20E-3 # [s]
f = 60 # [Hz]
theta = 45 # [graus]
Rs = 1E-3 # [Ohms] Resistência interna da fonte
Rload = 5 # [Ohms] Resistência da carga
Lp = 5E-3 # [H] indutância própria
Lm = 1E-3 # [H] indutância mútua

# Cáculo das cosntantes
w = 2*np.pi*f
N = round(tmax/dt)+1 #número de pontos da simulação

# inicialização das variáveis
t = np.linspace(0, tmax, N) #vetor de tempo
# CORREÇÃO: corrigida a criação da fonte de tensão trifásica
vs = np.array([Vm*np.cos(w*t+(theta*np.pi/180)),
               Vm*np.cos(w*t+(theta*np.pi/180)-(2*np.pi/3)),
               Vm*np.cos(w*t+(theta*np.pi/180)-(4*np.pi/3))]) # fonte de tensão

Gs = (1/Rs) * np.eye(3) #condutância da fonte
Gload = (1/Rload) * np.eye(3) #condutância da carga
L = [[Lm, Lp, Lp],[Lp, Lm, Lp],[Lp, Lp, Lm]] #matriz de indutâncias

Gl = np.linalg.inv(L) * dt/2 #matriz de condutâncias

G = [[Gs+Gl, -Gl], [-Gl, Gl+Gload]]

Il = [[0],[0],[0]]
iload = np.zeros((3,N))


for i in range(1,N):
    Is=Gs @ vs[:,i].reshape(3,1)
    vs=Rs @ [[Is-Il],[Il]]
    vk=vs[0:2,0].reshape(3,1)
    vm=vs[3:5,0].reshape(3,1)
    Il=2*Gl @ (vm-vk) + Il
    iload[0:2, i]= Gload @ vm




plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.plot(t, i, 'b-', linewidth=1.5)
plt.xlabel('Tempo (s)', fontsize=12)
plt.ylabel('Corrente (A)', fontsize=12)
plt.title('Corrente no indutor', fontsize=14)
plt.grid(alpha=0.3)
plt.xlim(0, tmax)
plt.legend()

plt.legend()

plt.tight_layout()
plt.show()


plt.tight_layout()
plt.show()