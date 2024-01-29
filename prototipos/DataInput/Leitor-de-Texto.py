from PyPDF2 import PdfReader
import re
import pandas as pd

# Abrir pedef em Binários.
with open("sample.pdf", 'rb') as file_pdf:
    reader_pdf = PdfReader(file_pdf)
    num_paginas = len(reader_pdf.pages)

    # padrao_origem = re.compile(r'Inscrição:\s*(.+?)\s*Origem:')
    # padrao_inscricao = re.compile(r'Matrícula:\s*(.+?)\s*Inscrição:')
    # padrao_matricula = re.compile(r'Endereço:.*?(\d{3}\.\d{3}\.\d{4}\.\d{3})\s*Matrícula:')
    # padrao_endereco = re.compile(r'Endereço:\s*(.+?)\s*(?=\d{3}\.\d{3}\.\d{4}\.\d{3}\s*Matrícula:)')
    # Ajustado para excluir o numero de Matrículas.
    # # padrao_data = re.compile(r'Origem:(.*?)Endereço:', re.DOTALL)
    # padrao_dividas = re.compile(r'Situação:\s*(.+?)\n\n', re.DOTALL)
    # padrao_situacao = re.compile(r'\n*(.+?)\s*Situação:')
    # padrao_linha = re.compile(r'(\d{4}) (\d{2}) (.*?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d+) (\d+)')

    imoveis = []
    total_solicitante = 0
    
    # Iterate through the pages of the PDF.
    for num_pagina in range(num_paginas):
        pagina = reader_pdf.pages[num_pagina]
        # Extração do texto das paginas.
        text = pagina.extract_text()
        # Debugging de leitura de arquivo.
        print(f"Texto da página {num_pagina + 1}:\n{text}\n")
        
        padrao_origem = re.compile(r'Inscrição:\s*(.+?)\s*Origem:')
        padrao_inscricao = re.compile(r'Matrícula:\s*(.+?)\s*Inscrição:')
        padrao_matricula = re.compile(r'Endereço:.*?(\d{3}\.\d{3}\.\d{4}\.\d{3})\s*Matrícula:' or r'Endereco:\..*?(\d{4})')
        padrao_endereco = re.compile(r'Endereço:\s*(.+?)\s*(?=\d{3}\.\d{3}\.\d{4}\.\d{3}\s*Matrícula:)')

        # Correspondencia de Headers.
        correspondencia_origem = padrao_origem.findall(text)
        correspondencia_inscricao = padrao_inscricao.findall(text)
        correspondencia_matricula = padrao_matricula.findall(text)
        correspondencia_endereco = padrao_endereco.findall(text)

        # Processamento de correspondencias.
        for origem, inscricao, endereco, matricula in zip(
            correspondencia_origem,
            correspondencia_inscricao,
            correspondencia_endereco,
            correspondencia_matricula
        ):
            origem = origem.strip()
            inscricao = inscricao.strip()
            matricula = matricula.strip()
            matricula = matricula.strip() if matricula else False
            endereco = endereco.strip()
            
            padrao_data = re.compile(r'Origem:(.*?)Endereço:', re.DOTALL) or re.compile(r'Origem:(.*?)OBSERVAÇÃO:', re.DOTALL)
            data = padrao_data.search(text).group(1).strip()
            # correspondencia_data = padrao_data.search(text)
            # if correspondencia_data:
            #     # Obterndo correspondencia de dados.
            #     data = correspondencia_data.group(1).strip()
            # else:
            #     data = "Padrão de dados em 'data' não encontrado."
            # # Formatando os dados.
            data = re.sub(r'\.(\s*\.)+', '', data)
            data = re.sub(r'ANO MÊS TRIBUTO VL. ATUAL. JUROS MULTA TOTAL VENCIDAS / A VENCER', '', data)
            data = re.sub(r'^.*TOTAL:$', '', data, flags=re.MULTILINE)
            data = re.sub(r'^TOTAL ORIGEM:.*$', '', data, flags=re.MULTILINE)
              
            padrao_dividas = re.compile(r'Situação:\s*(.+?)\n\n', re.DOTALL)
            padrao_situacao = re.compile(r'\n*(.+?)\s*Situação:')
            correspondencia_situacao = padrao_situacao.findall(data)
            correspondencia_dividas = padrao_dividas.findall(data)
            
            situacao = correspondencia_situacao[0].strip() if correspondencia_situacao else None
            dividas = []
            total_origem = 0
            
            if correspondencia_dividas and correspondencia_situacao:
                for dividas_cliente in correspondencia_dividas:
                    divida = []
                    total_divida = 0       
                    for linha in dividas_cliente.strip().split('\n'):
                        padrao_linha = re.compile(r'(\d{4}) (\d{2}) (.*?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d+) (\d+)')
                        correspondencia_linha = padrao_linha.match(linha)
                        if correspondencia_linha:
                            # ano, mes, tributo, float(valor_atual), float(juros), float(multa), float(total), int(vencidas), int(a_vencer) = correspondencia_linha.groups()
                            ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer = correspondencia_linha.groups()
                            valor_atual = valor_atual.replace(".", "").replace(",",".")
                            juros = juros.replace(".", "").replace(",", ".")
                            multa = multa.replace(".", "").replace(",",".")
                            total = total.replace(".", "").replace(",",".")
                            ano, mes, tributo = map(str, [ano, mes, tributo])
                            valor_atual, juros, multa = map(float, [valor_atual, juros, multa])
                            # total = valor_atual + juros + multa = map(float, )
                            vencidas, a_vencer = map(int, [vencidas, a_vencer])
                            total_divida += float(total)
                            divida.append({
                                "Ano": ano,
                                "Mês": mes,
                                "Tributo": tributo,
                                "Valor Atual": valor_atual,
                                "Juros": juros,
                                "Multa": multa,
                                "Total": total,
                                "Vencidas": vencidas,
                                "A Vencer": a_vencer
                            })
                            #  ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer = correspondencia_linha.groups()
                            #  valor_atual = valor_atual.replace(".", "").replace(",",".")
                            #  juros = juros.replace(".", "").replace(",", ".")
                            #  multa = multa.replace(".", "").replace(",",".")
                            #  total = total.replace(".", "").replace(",",".")
                            #  detalhes_divida.append([ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer])
                        # else:
                        #     detalhes_divida.append([ano or None, mes or None, tributo or None, valor_atual or None, juros or None, multa or None, total or None, vencidas or None, a_vencer or None])
                    total_origem += float(total_divida)
                    dividas.append({
                        "Situação": situacao, 
                        "Divida": divida,
                        "Total Origem": total_origem
                    })
            
            imoveis.append({
                "Origem": origem,
                "Inscrição": inscricao,
                "Matrícula": matricula,
                "Endereço": endereco,
                "Dívidas": dividas,
                # "Data": data
            })
            
            total_solicitante += float(total_origem)

# Depuração de resultados.
for i, imovel in enumerate(imoveis, start=1):
    origem = imovel['Origem']
    inscricao = imovel['Inscrição']
    matricula = imovel['Matrícula']
    endereco = imovel['Endereço']
    dividas = imovel['Dívidas']

    print(f"{i}\nOrigem: {origem} Inscrição: {inscricao} Matricula: {matricula}  \nEndereço: {endereco} \nDividas: {dividas}\n")
    print(f"Total Solicitante: {total_solicitante}")
# Criar DataFrame
df = pd.DataFrame(imoveis, columns=["Origem", "Inscrição",  "Endereço", "Dívidas"])

# Transformar a coluna "Dívidas" em string para evitar problemas com listas
# df["Dívidas"] = df["Dívidas"].astype(str)

# Depuração do DataFrame
print("\n", df)

# Salvando arquivo .CSV
df.to_csv("Relatório.csv", index=False)
print("Arquivo CSV Salvo com sucesso!")

# Salvando arquivo em formato Excel
Excel = "Relatório.xlsx"
df.to_excel(Excel, index=False)
print("Excel Salvo com sucesso!")