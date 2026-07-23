import numpy as np
import matplotlib.pyplot as plt
from scipy.special import iv as besseli

# Constantes
mu0 = 4 * np.pi * 1e-7
eps0 = 8.85418782e-12


H = 20
r = 5e-3
G = 1.5e-12
sigma = 3.8e7
rho = [10, 100, 1000]


f = np.logspace(0, 8, 500)
w = 2 * np.pi * f


Lext = mu0 * np.log(2 * H / r) / (2 * np.pi)
Zext = 1j * w * Lext


arg = np.sqrt(1j * w * mu0 * sigma) * r
Zint = (1 / (2 * np.pi * r)) * np.sqrt(1j * w * mu0 / sigma) * besseli(0, arg) / besseli(1, arg)

Zsolo = np.zeros((len(rho), len(f)), dtype=complex)

for i, rho_val in enumerate(rho):
    p = np.sqrt(rho_val / (1j * w * mu0))
    Zsolo[i, :] = 1j * f * mu0 * np.log((H + p) / H)

# Impedância total
Z = Zext + Zint + Zsolo

C = eps0 * mu0 / Lext
Y = G + 1j * w * C

gamma = np.sqrt(Z * Y)
alpha = np.real(gamma)
beta = np.imag(gamma)

vf = np.zeros_like(beta)

for i in range(len(rho)):
    for k in range(len(f)):
        if beta[i, k] != 0:
            vf[i, k] = w[k] / beta[i, k]


Zc = np.abs(np.sqrt(Z / Y))


plt.figure(figsize=(10, 6))

plt.loglog(f, alpha[0, :], 'k', linewidth=2, label='10 Ω m')
plt.loglog(f, alpha[1, :], 'b', linewidth=2, label='100 Ω m')
plt.loglog(f, alpha[2, :], 'g', linewidth=2, label='1000 Ω m')

plt.axis([1, 1e8, 1e-7, 1e-1])
plt.xlabel('Frequência (Hz)')
plt.ylabel('Constante de Propagação (m⁻¹)')
plt.title('Constante de Atenuação')
plt.legend(loc='upper left')
plt.grid(True, which='both', alpha=0.3)
plt.tight_layout()


plt.figure(figsize=(10, 6))

plt.semilogx(f, vf[0, :], 'k', linewidth=2, label='10 Ω m')
plt.semilogx(f, vf[1, :], 'b', linewidth=2, label='100 Ω m')
plt.semilogx(f, vf[2, :], 'g', linewidth=2, label='1000 Ω m')

plt.xlim([1, 1e8])
plt.xlabel('Frequência (Hz)')
plt.ylabel('Velocidade de Fase (m/s)')
plt.title('Velocidade de Fase')
plt.legend(loc='lower right')
plt.grid(True, which='both', alpha=0.3)
plt.tight_layout()


plt.figure(figsize=(10, 6))

plt.semilogx(f, Zc[0, :], 'k', linewidth=2, label='10 Ω m')
plt.semilogx(f, Zc[1, :], 'b', linewidth=2, label='100 Ω m')
plt.semilogx(f, Zc[2, :], 'g', linewidth=2, label='1000 Ω m')

plt.axis([1, 1e8, 400, 1100])
plt.xlabel('Frequência (Hz)')
plt.ylabel('|Zc| (Ω)')
plt.title('Impedância Característica')
plt.legend(loc='upper right')
plt.grid(True, which='both', alpha=0.3)
plt.tight_layout()


plt.show()
