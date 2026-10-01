import os
import re
import textwrap
import unicodedata

import openpyxl
from openpyxl.utils import column_index_from_string


def normalize_ascii(texto):
    """
    Converte letras acentuadas e alguns caracteres especiais para
    equivalentes ASCII, evitando dependência de suporte a UTF-8
    na impressora Zebra.
    """
    special_map = {
        "ß": "ss",
        "ẞ": "SS",
        "Æ": "AE",
        "æ": "ae",
        "Œ": "OE",
        "œ": "oe",
        "Ø": "O",
        "ø": "o",
        "Ł": "L",
        "ł": "l",
        "Đ": "D",
        "đ": "d",
        "Ð": "D",
        "ð": "d",
        "Þ": "TH",
        "þ": "th",
    }

    texto = "".join(special_map.get(char, char) for char in str(texto))
    decomposed = unicodedata.normalize("NFKD", texto)

    return "".join(
        char
        for char in decomposed
        if not unicodedata.combining(char) and ord(char) < 128
    )


def formatar_acentos_zpl(texto):
    """
    Normaliza o texto para ASCII e escapa caracteres que podem
    interferir na sintaxe ZPL.

    O modelo atual usa ^FH\\ nos campos ^FD, portanto os códigos
    hexadecimais abaixo são interpretados pela impressora.
    """
    if not texto:
        return ""

    texto = normalize_ascii(texto)

    return (
        texto
        .replace("\\", "\\5C")
        .replace("^", "\\5E")
        .replace("~", "\\7E")
    )


def aplicar_substituicao_zpl(modelo_zpl, texto_alvo, texto_novo, usar_quebra):
    """
    Substitui o marcador no ZPL.

    Quando a quebra automática está ativa, divide o texto
    e incrementa a posição Y em 40 pontos por linha.
    """

    if not usar_quebra:
        return modelo_zpl.replace(texto_alvo, texto_novo)

    padrao = re.compile(
        rf"(\^(?:FT|FO)\d+,)(\d+)(.*?\^FD)"
        rf"({re.escape(texto_alvo)})(\^FS)",
        re.IGNORECASE,
    )

    def replacer(match):
        prefixo_x = match.group(1)
        y_inicial = int(match.group(2))
        configuracoes = match.group(3)
        sufixo = match.group(5)

        largura_maxima = max(len(texto_alvo), 1)

        linhas_texto = textwrap.wrap(
            texto_novo, width=largura_maxima, break_long_words=True
        )

        blocos_zpl = []

        for indice, linha in enumerate(linhas_texto):
            y_atual = y_inicial + (indice * 40)

            blocos_zpl.append(f"{prefixo_x}{y_atual}{configuracoes}{linha}{sufixo}")

        return "\n".join(blocos_zpl)

    if padrao.search(modelo_zpl):
        return padrao.sub(replacer, modelo_zpl)

    # Substituição alternativa caso a estrutura ZPL não seja encontrada
    return modelo_zpl.replace(texto_alvo, texto_novo)


def validar_mapeamentos(mapeamentos):
    """
    Valida os marcadores e converte as letras das colunas
    do Excel em índices numéricos.
    """

    if not mapeamentos:
        raise ValueError("Adicione pelo menos um marcador antes de processar.")

    pares_validos = []

    for mapeamento in mapeamentos:
        alvo = str(mapeamento.get("marker", "")).strip()
        coluna = str(mapeamento.get("column", "")).strip().upper()

        if not alvo or not coluna:
            raise ValueError("Preencha todos os marcadores e suas colunas.")

        try:
            indice_coluna = column_index_from_string(coluna) - 1
        except ValueError:
            raise ValueError(f"Letra de coluna inválida: {coluna}")

        pares_validos.append((alvo, indice_coluna))

    return pares_validos


def processar_arquivos(
    caminho_modelo, caminho_excel, diretorio_saida, mapeamentos, usar_quebra=True
):
    """
    Processa o modelo PRN utilizando os dados de uma planilha Excel.

    Gera um arquivo PRN para cada aba que possuir registros válidos.

    Retorna um resumo da operação.
    """

    # Validação dos arquivos
    if not caminho_modelo or not os.path.isfile(caminho_modelo):
        raise FileNotFoundError("Selecione um arquivo de modelo PRN válido.")

    if not caminho_excel or not os.path.isfile(caminho_excel):
        raise FileNotFoundError("Selecione uma planilha Excel válida.")

    if not diretorio_saida or not os.path.isdir(diretorio_saida):
        raise FileNotFoundError("Selecione uma pasta de saída válida.")

    pares_validos = validar_mapeamentos(mapeamentos)

    # Lê o modelo PRN
    with open(caminho_modelo, "r", encoding="utf-8-sig") as arquivo:
        modelo_base = arquivo.read().replace("\ufeff", "")

    # Abre a planilha
    workbook = openpyxl.load_workbook(caminho_excel, data_only=True, read_only=True)

    arquivos_gerados = []
    total_etiquetas = 0

    try:
        for nome_aba in workbook.sheetnames:
            planilha = workbook[nome_aba]

            lote_zpl_final = []
            contador_etiquetas = 0

            indice_principal = pares_validos[0][1]

            for linha in planilha.iter_rows(min_row=1, values_only=True):
                # Verifica se a linha possui o dado principal
                dado_principal = (
                    linha[indice_principal] if indice_principal < len(linha) else None
                )

                if dado_principal is None or str(dado_principal).strip() == "":
                    continue

                # Inicia uma etiqueta baseada no modelo original
                etiqueta_pronta = modelo_base

                # Substitui todos os marcadores configurados
                for alvo, indice_coluna in pares_validos:
                    dado = linha[indice_coluna] if indice_coluna < len(linha) else ""

                    if dado is None:
                        dado = ""

                    texto_formatado = formatar_acentos_zpl(str(dado).strip())

                    etiqueta_pronta = aplicar_substituicao_zpl(
                        etiqueta_pronta, alvo, texto_formatado, usar_quebra
                    )

                # Remove marcas BOM que possam ter vindo do modelo ou dos dados.\n                etiqueta_pronta = etiqueta_pronta.replace("\ufeff", "")\n\n                lote_zpl_final.append(etiqueta_pronta)
                contador_etiquetas += 1

            # Gera arquivo somente se houver etiquetas
            if contador_etiquetas > 0:
                nome_arquivo_seguro = "".join(
                    caractere
                    for caractere in str(nome_aba)
                    if caractere.isalnum() or caractere in (" ", "_", "-")
                ).strip()

                if not nome_arquivo_seguro:
                    nome_arquivo_seguro = "Aba"

                caminho_saida = os.path.join(
                    diretorio_saida, f"{nome_arquivo_seguro}.prn"
                )

                with open(
                    caminho_saida,
                    "w",
                    encoding="ascii",
                    errors="strict",
                    newline="\n",
                ) as arquivo:
                    arquivo.write("\n".join(lote_zpl_final) + "\n")

                arquivos_gerados.append(
                    {
                        "aba": nome_aba,
                        "caminho": caminho_saida,
                        "etiquetas": contador_etiquetas,
                    }
                )

                total_etiquetas += contador_etiquetas

    finally:
        workbook.close()

    return {
        "arquivos_gerados": arquivos_gerados,
        "total_arquivos": len(arquivos_gerados),
        "total_etiquetas": total_etiquetas,
    }
