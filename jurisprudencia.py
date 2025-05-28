# jurisprudencia.py
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def buscar_jurisprudencia_tjgo(termo_pesquisa, max_resultados=3):
    """
    Busca jurisprudência no site do TJGO e retorna os primeiros 'max_resultados'.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Executa o Chrome em modo headless (sem interface gráfica)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("window-size=1200x600") # Pode ajudar em alguns casos headless

    # Instala e gerencia o ChromeDriver automaticamente
    try:
        service = ChromeService(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        return [{"erro_driver": f"Falha ao iniciar o WebDriver: {str(e)}"}]

    resultados_finais = []
    try:
        navegador.get("https://projudi.tjgo.jus.br/ConsultaJurisprudencia")

        # Espera o campo de texto estar presente e visível
        campo_pesquisa_elemento = WebDriverWait(navegador, 10).until(
            EC.visibility_of_element_located((By.ID, "Texto"))
        )
        campo_pesquisa_elemento.send_keys(termo_pesquisa)
        time.sleep(0.5) # Pequena pausa após digitar

        # Espera o botão estar clicável
        botao_elemento = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.ID, "formLocalizarBotao"))
        )
        # Tenta clicar via JavaScript se o clique normal falhar ou para garantir visibilidade
        navegador.execute_script("arguments[0].scrollIntoView(true);", botao_elemento)
        time.sleep(0.5) # Pequena pausa após scroll
        botao_elemento.click()

        # Espera os resultados aparecerem (aqui um exemplo, pode precisar de ajuste)
        WebDriverWait(navegador, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "search-result"))
        )
        time.sleep(1) # Dá um tempo extra para o conteúdo carregar completamente

        blocos_de_resultado = navegador.find_elements(By.CLASS_NAME, "search-result")

        if blocos_de_resultado:
            for indice, bloco_individual in enumerate(blocos_de_resultado[:max_resultados]):
                try:
                    # Scroll para o elemento para garantir que está "visível" para o Selenium
                    # navegador.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'auto'});", bloco_individual)
                    # time.sleep(0.2) # Pausa para o scroll

                    texto_do_bloco = bloco_individual.text
                    if not texto_do_bloco.strip(): # Verifica se o texto não está vazio
                        texto_do_bloco = "Conteúdo do bloco não pôde ser extraído ou estava vazio."

                    resultados_finais.append({"id": indice + 1, "texto": texto_do_bloco})
                except Exception as e:
                    resultados_finais.append({"id": indice + 1, "erro": f"Erro ao processar bloco {indice + 1}: {str(e)}", "texto": ""})
        else:
            resultados_finais.append({"info": f"Nenhum resultado encontrado para: '{termo_pesquisa}'"})

    except Exception as e:
        resultados_finais.append({"erro_geral": f"Erro durante a busca: {str(e)}"})
    finally:
        navegador.quit()

    return resultados_finais

if __name__ == "__main__":
    if len(sys.argv) > 1:
        termo = sys.argv[1]
        resultados = buscar_jurisprudencia_tjgo(termo)
        # Imprime o resultado como JSON para ser capturado pelo script principal
        print(json.dumps(resultados, ensure_ascii=False))
    else:
        # Erro se nenhum termo for passado via linha de comando
        print(json.dumps([{"erro": "Nenhum termo de busca fornecido."}], ensure_ascii=False))