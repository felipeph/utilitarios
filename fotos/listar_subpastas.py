
import os
import argparse

def listar_subpastas(root_path):
    """
    Lista todas as subpastas recursivamente a partir de um diretório raiz
    e salva a lista em um arquivo de texto.
    """
    subpastas_encontradas = []
    print(f"Analisando o diretório: {root_path}")

    # os.walk() gera os nomes dos arquivos e diretórios em uma árvore de diretórios.
    for dirpath, dirnames, _ in os.walk(root_path):
        # A primeira iteração (dirpath == root_path) lista as pastas do primeiro nível.
        # As iterações seguintes exploram as subpastas.
        for subpasta in dirnames:
            caminho_completo = os.path.join(dirpath, subpasta)
            subpastas_encontradas.append(caminho_completo)

    if not subpastas_encontradas:
        print("Nenhuma subpasta foi encontrada.")
        return

    # Define o nome do arquivo de saída
    arquivo_saida = os.path.join(root_path, "subpastas.txt")

    try:
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            for caminho in sorted(subpastas_encontradas): # Salva em ordem alfabética
                f.write(caminho + '\n')
        print(f"\nSucesso! {len(subpastas_encontradas)} subpastas listadas em: {arquivo_saida}")
    except IOError as e:
        print(f"\n[Erro] Não foi possível escrever o arquivo de saída: {e}")

if __name__ == "__main__":
    # Configura o parser de argumentos da linha de comando
    parser = argparse.ArgumentParser(
        description="Lista todas as subpastas de um determinado diretório e salva o resultado em um arquivo 'subpastas.txt'.",
        epilog="Se nenhum caminho for fornecido, o script analisará a pasta onde ele mesmo está localizado."
    )
    parser.add_argument(
        "path",
        nargs="?",  # O argumento do caminho é opcional
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Caminho da pasta a ser analisada. O padrão é o diretório do script."
    )
    args = parser.parse_args()

    target_path = args.path

    # Verifica se o caminho existe e é um diretório
    if not os.path.isdir(target_path):
        print(f"[Erro] O caminho especificado não é um diretório válido: {target_path}")
    else:
        listar_subpastas(target_path)
