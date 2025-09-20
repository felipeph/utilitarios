
import argparse
import os
import sys

def listar_arquivos_por_extensao(diretorio, extensao):
    """
    Lista os arquivos em um diretório que correspondem a uma determinada extensão.

    Args:
        diretorio (str): O caminho para o diretório a ser pesquisado.
        extensao (str): A extensão do arquivo a ser filtrada (sem o ponto).
    """
    # Garante que a extensão não tenha um ponto no início e seja minúscula
    extensao_limpa = extensao.lower().lstrip('.')

    print(f"Buscando por arquivos com a extensão '.{extensao_limpa}' em: '{diretorio}'\n")

    arquivos_encontrados = []
    try:
        # Lista todos os itens no diretório especificado
        for item in os.listdir(diretorio):
            # Cria o caminho completo para o item
            caminho_completo = os.path.join(diretorio, item)
            # Verifica se é um arquivo e se a extensão corresponde (case-insensitive)
            if os.path.isfile(caminho_completo) and item.lower().endswith(f'.{extensao_limpa}'):
                arquivos_encontrados.append(item)
    except FileNotFoundError:
        print(f"Erro: O diretório '{diretorio}' não foi encontrado.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ocorreu um erro: {e}", file=sys.stderr)
        sys.exit(1)

    if arquivos_encontrados:
        # Define o nome do arquivo de saída no diretório de busca
        nome_arquivo_saida = os.path.join(diretorio, f"listar_{extensao_limpa}.txt")
        
        try:
            # Garante que a lista esteja ordenada
            arquivos_ordenados = sorted(arquivos_encontrados)
            
            # Escreve a lista de arquivos no arquivo de saída
            with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
                for arquivo in arquivos_ordenados:
                    f.write(f"{arquivo}\n")
            
            print(f"Sucesso! {len(arquivos_ordenados)} arquivos encontrados.")
            print(f"A lista foi salva em: {nome_arquivo_saida}")

        except Exception as e:
            print(f"Erro ao salvar o arquivo de saída: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Nenhum arquivo encontrado com esta extensão.")

if __name__ == "__main__":
    # Define o diretório do script como o padrão para a busca
    diretorio_padrao = os.path.dirname(os.path.abspath(__file__))

    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(
        description="Lista arquivos com uma extensão específica em um diretório, ignorando maiúsculas/minúsculas.",
        formatter_class=argparse.RawTextHelpFormatter # Melhora a formatação da ajuda
    )

    parser.add_argument(
        '-p', '--path',
        dest='diretorio',
        default=diretorio_padrao,
        help=f"Caminho do diretório para a busca.\n(Padrão: {diretorio_padrao})"
    )

    parser.add_argument(
        '-e', '--ext',
        dest='extensao',
        required=True,
        help="Extensão do arquivo para filtrar (ex: 'mp4', 'txt', 'jpg')."
    )

    # Analisa os argumentos fornecidos
    args = parser.parse_args()

    # Chama a função principal com os argumentos
    listar_arquivos_por_extensao(args.diretorio, args.extensao)
