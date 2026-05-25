import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import tempfile

# Caminho do executável do FEMM
CAMINHO_FEMM = r"C:\femm42\bin\femm.exe"


def criar_simulacao_bobina(material_isolante, permissividade_relativa):
    """
    Cria um script Lua e o executa no FEMM em modo batch.
    """
    posicoes = []
    campos = []

    # Verifica se o FEMM existe
    if not os.path.exists(CAMINHO_FEMM):
        print(f"ERRO CRÍTICO: FEMM não encontrado em {CAMINHO_FEMM}")
        return np.array(posicoes), np.array(campos)

    # --- Conteúdo do Script Lua OTIMIZADO ---
    script_lua = f'''-- Script para simulação de bobina em {material_isolante}
-- Modo batch: sem interface gráfica desnecessária

-- Desabilita a janela de progresso para execução mais rápida
hideconsole()

-- 1. Cria um novo documento eletrostático
newdocument(0)

-- 2. Definição dos Materiais
mi_addmaterial("Ar", 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
mi_addmaterial("Oleo", {permissividade_relativa}, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
mi_addmaterial("Cobre", 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)

-- 3. Geometria (em mm)
raio_interno = 10
raio_externo = 20
raio_dominio = 50
tensao = 1000

-- Desenha o domínio externo
mi_drawcircle(0, 0, raio_dominio, 0, 360)
mi_selectcircle(0, 0, raio_dominio, 4)
mi_setblockprop("{material_isolante}", 1, 0, "<None>", 0, 0, 0)
mi_clearselected()

-- Desenha a Bobina (Anel)
mi_drawcircle(0, 0, raio_interno, 0, 360)
mi_drawcircle(0, 0, raio_externo, 0, 360)
raio_medio = (raio_interno + raio_externo) / 2
mi_selectcircle(0, 0, raio_medio, 4)
mi_setblockprop("Cobre", 1, 0, "<None>", 0, 0, 0)
mi_clearselected()

-- 4. Condições de Contorno
mi_selectcircle(0, 0, raio_dominio, 4)
mi_setnodeprop(0, "0 Volts")
mi_clearselected()

mi_selectcircle(0, 0, raio_medio, 4)
mi_setnodeprop(tensao, "Bobina HV")
mi_clearselected()

-- 5. Configuração do Problema
mi_probdef(0, "millimeters", "planar", 1e-8, 0, 30)

-- Salva o problema
mi_saveas("{material_isolante}_bobina.fem")

-- Executa a análise (0 = sem janela de progresso)
mi_analyze(0)

-- Carrega a solução
mi_loadsolution()

-- 6. Extração dos Resultados
resultados_file = "{material_isolante}_resultados.txt"
arquivo = io.open(resultados_file, "w")

if arquivo ~= nil then
    passo = (raio_externo - raio_interno) / 100
    for r = raio_interno, raio_externo, passo do
        x = r
        y = 0
        sucesso, V, Ex, Ey = mo_getpointvalues(x, y)
        if sucesso == 0 then
            E_mag = math.sqrt(Ex*Ex + Ey*Ey)
            arquivo:write(string.format("%f %f\\n", r, E_mag))
        end
    end
    arquivo:close()
end

-- Fecha o FEMM
mi_close()
'''

    print(f"  Executando simulação para {material_isolante}...")

    # Cria um arquivo para o script Lua na pasta atual (não temporária)
    script_path = f"script_{material_isolante}_{int(time.time())}.lua"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_lua)

    try:
        # Executa o FEMM em modo batch (sem interface)
        # Usar -lua-script com caminho absoluto
        comando = [CAMINHO_FEMM, f'-lua-script={os.path.abspath(script_path)}']

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=60,  # 60 segundos é suficiente
            shell=False
        )

        # Verificar se houve erro na execução
        if resultado.returncode != 0:
            print(f"    Código de erro: {resultado.returncode}")

        # Mostrar saída para debug
        if resultado.stdout:
            print(f"    Saída: {resultado.stdout[:200]}")

        # Ler o arquivo de resultados
        resultados_path = f"{material_isolante}_resultados.txt"

        if os.path.exists(resultados_path):
            with open(resultados_path, 'r') as res_file:
                for linha in res_file:
                    partes = linha.strip().split()
                    if len(partes) == 2:
                        posicoes.append(float(partes[0]))
                        campos.append(float(partes[1]))
            os.remove(resultados_path)
            print(f"    ✓ Simulação finalizada. {len(posicoes)} pontos extraídos.")
        else:
            print(f"    ✗ Arquivo de resultados não encontrado.")
            # Listar arquivos na pasta para debug
            arquivos = os.listdir('.')
            print(f"    Arquivos na pasta: {[f for f in arquivos if f.endswith('.txt')]}")

    except subprocess.TimeoutExpired:
        print(f"    ✗ ERRO: Tempo limite excedido (60s) para {material_isolante}.")
    except Exception as e:
        print(f"    ✗ ERRO FATAL: {e}")
    finally:
        # Limpa os arquivos temporários
        if os.path.exists(script_path):
            os.remove(script_path)

        fem_file = f"{material_isolante}_bobina.fem"
        if os.path.exists(fem_file):
            os.remove(fem_file)

    return np.array(posicoes), np.array(campos)


def testar_femm_manualmente():
    """
    Testa se o FEMM está funcionando corretamente
    """
    print("\n" + "=" * 60)
    print("TESTE MANUAL DO FEMM")
    print("=" * 60)

    script_teste = '''hideconsole()
newdocument(0)
mi_addmaterial("Teste", 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
mi_drawcircle(0, 0, 10, 0, 360)
mi_saveas("teste_femm.fem")
mi_close()
print("SUCESSO: FEMM funcionou corretamente")
'''

    script_path = "teste_femm.lua"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_teste)

    try:
        print(f"Executando teste com: {CAMINHO_FEMM}")
        resultado = subprocess.run(
            [CAMINHO_FEMM, f'-lua-script={os.path.abspath(script_path)}'],
            capture_output=True,
            text=True,
            timeout=30
        )

        print(f"Retorno: {resultado.returncode}")
        if resultado.stdout:
            print(f"Saída: {resultado.stdout}")
        if resultado.stderr:
            print(f"Erro: {resultado.stderr}")

        if os.path.exists("teste_femm.fem"):
            print("✓ Arquivo .fem criado com sucesso!")
            os.remove("teste_femm.fem")
        else:
            print("✗ Arquivo .fem NÃO foi criado")

    except subprocess.TimeoutExpired:
        print("✗ Teste expirou - FEMM pode estar travado")
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

    print("=" * 60 + "\n")


def simular_com_entrada_manual():
    """
    Simulação alternativa: gera arquivo .fem manualmente e pede para o usuário
    executar a simulação no FEMM
    """
    print("\n" + "=" * 60)
    print("MODO MANUAL - Simulação com FEMM")
    print("=" * 60)
    print("\nEste modo irá gerar arquivos .fem que você pode abrir manualmente no FEMM")

    for material, permissividade in [("Ar", 1.0), ("Oleo", 2.2)]:
        print(f"\nGerando arquivo para {material}...")

        script_lua = f'''newdocument(0)
mi_addmaterial("Ar", 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
mi_addmaterial("Oleo", {permissividade}, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
mi_addmaterial("Cobre", 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)

raio_interno = 10
raio_externo = 20
raio_dominio = 50
tensao = 1000

mi_drawcircle(0, 0, raio_dominio, 0, 360)
mi_selectcircle(0, 0, raio_dominio, 4)
mi_setblockprop("{material}", 1, 0, "<None>", 0, 0, 0)
mi_clearselected()

mi_drawcircle(0, 0, raio_interno, 0, 360)
mi_drawcircle(0, 0, raio_externo, 0, 360)
raio_medio = (raio_interno + raio_externo) / 2
mi_selectcircle(0, 0, raio_medio, 4)
mi_setblockprop("Cobre", 1, 0, "<None>", 0, 0, 0)
mi_clearselected()

mi_selectcircle(0, 0, raio_dominio, 4)
mi_setnodeprop(0, "0 Volts")
mi_clearselected()

mi_selectcircle(0, 0, raio_medio, 4)
mi_setnodeprop(tensao, "Bobina HV")
mi_clearselected()

mi_probdef(0, "millimeters", "planar", 1e-8, 0, 30)
mi_saveas("{material}_bobina.fem")
mi_close()
'''
        script_path = f"gerar_{material}.lua"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_lua)

        subprocess.run([CAMINHO_FEMM, f'-lua-script={os.path.abspath(script_path)}'],
                       capture_output=True, timeout=30)

        if os.path.exists(f"{material}_bobina.fem"):
            print(f"  ✓ Arquivo {material}_bobina.fem criado com sucesso!")

        os.remove(script_path)

    print("\nArquivos criados:")
    print("  - Ar_bobina.fem")
    print("  - Oleo_bobina.fem")
    print("\nPara prosseguir:")
    print("1. Abra cada arquivo no FEMM manualmente")
    print("2. Execute a análise (Problem -> Analyze)")
    print("3. Use o pós-processador para extrair os resultados")

    return np.array([]), np.array([]), np.array([]), np.array([])


def main():
    print("=" * 60)
    print("SIMULAÇÃO FEMM: AR vs ÓLEO ISOLANTE")
    print("=" * 60)

    # Verifica se o FEMM existe
    if not os.path.exists(CAMINHO_FEMM):
        print(f"\nERRO: FEMM não encontrado em {CAMINHO_FEMM}")
        return

    print(f"\nFEMM encontrado em: {CAMINHO_FEMM}")

    # Pergunta o modo de operação
    print("\nEscolha o modo de operação:")
    print("1 - Automático (tenta executar a simulação diretamente)")
    print("2 - Testar FEMM (verifica se está funcionando)")
    print("3 - Modo manual (gera arquivos .fem para abrir no FEMM)")

    opcao = input("\nDigite sua opção (1/2/3): ").strip()

    if opcao == "1":
        print("\nIniciando simulações automáticas...\n")

        # Simulação para o Ar
        print("[1/2] Ar (εr = 1.0)")
        r_ar, E_ar = criar_simulacao_bobina("Ar", 1.0)

        # Simulação para o Óleo
        print("\n[2/2] Óleo Mineral (εr = 2.2)")
        r_oleo, E_oleo = criar_simulacao_bobina("Oleo", 2.2)

        # Verificação de Sucesso
        if len(E_ar) == 0 or len(E_oleo) == 0:
            print("\nFalha nas simulações. Tente o modo manual (opção 3).")
            return

        # Exibir resultados
        E_max_ar = np.max(E_ar)
        E_max_oleo = np.max(E_oleo)

        print("\n" + "=" * 60)
        print("RESULTADOS")
        print("=" * 60)
        print(f"Campo Máximo no AR:     {E_max_ar:.2f} V/mm")
        print(f"Campo Máximo no ÓLEO:   {E_max_oleo:.2f} V/mm")

        # Gráfico
        plt.figure(figsize=(10, 6))
        plt.plot(r_ar, E_ar, 'b-o', label='Ar', markersize=3)
        plt.plot(r_oleo, E_oleo, 'r-s', label='Óleo', markersize=3)
        plt.xlabel('Distância Radial (mm)')
        plt.ylabel('Campo Elétrico (V/mm)')
        plt.title('Comparação: Ar vs Óleo Isolante')
        plt.legend()
        plt.grid(True)
        plt.show()

    elif opcao == "2":
        testar_femm_manualmente()

    elif opcao == "3":
        simular_com_entrada_manual()

    else:
        print("Opção inválida!")


if __name__ == "__main__":
    main()