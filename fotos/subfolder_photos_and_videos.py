
import os
import shutil
import argparse

# Definição de extensões de arquivo de imagem e vídeo
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg']
VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.mpg', '.mpeg']

def organize_directory(directory_path):
    """
    Organiza os arquivos de um diretório em subpastas 'fotos' e 'videos'.
    """
    if not os.path.isdir(directory_path):
        print(f"Aviso: O diretório '{directory_path}' não foi encontrado. Pulando.")
        return

    print(f"\nProcessando o diretório: {directory_path}")

    # Criar subpastas para fotos e vídeos se não existirem
    photos_path = os.path.join(directory_path, 'fotos')
    videos_path = os.path.join(directory_path, 'videos')
    os.makedirs(photos_path, exist_ok=True)
    os.makedirs(videos_path, exist_ok=True)

    # Listar todos os arquivos no diretório
    for filename in os.listdir(directory_path):
        source_path = os.path.join(directory_path, filename)

        # Pular se for um diretório
        if not os.path.isfile(source_path):
            continue

        # Obter a extensão do arquivo em minúsculas
        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension.lower()

        # Mover o arquivo para a pasta correspondente
        try:
            if file_extension in IMAGE_EXTENSIONS:
                destination_path = os.path.join(photos_path, filename)
                shutil.move(source_path, destination_path)
                print(f"  [FOTO]   '{filename}' movido para '{photos_path}'")
            elif file_extension in VIDEO_EXTENSIONS:
                destination_path = os.path.join(videos_path, filename)
                shutil.move(source_path, destination_path)
                print(f"  [VÍDEO]  '{filename}' movido para '{videos_path}'")
        except shutil.Error as e:
            print(f"  [ERRO]   Não foi possível mover '{filename}'. Motivo: {e}")
        except Exception as e:
            print(f"  [ERRO]   Ocorreu um erro inesperado com o arquivo '{filename}': {e}")

def main():
    """
    Função principal para analisar argumentos e iniciar a organização.
    """
    parser = argparse.ArgumentParser(
        description="Organiza arquivos de mídia em subpastas 'fotos' and 'videos'.",
        epilog="Exemplo de uso: python organize_media.py 'C:\\caminho\\para\\pasta_ou_arquivo.txt'"
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="O caminho absoluto para um diretório ou para um arquivo .txt contendo uma lista de diretórios."
    )
    args = parser.parse_args()

    input_path = args.input_path
    directories_to_process = []

    if input_path.lower().endswith('.txt'):
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                directories_to_process = [line.strip() for line in f if line.strip()]
            if not directories_to_process:
                print("O arquivo de texto está vazio ou não contém caminhos válidos.")
                return
        except FileNotFoundError:
            print(f"Erro: O arquivo '{input_path}' não foi encontrado.")
            return
    else:
        directories_to_process.append(input_path)

    for directory in directories_to_process:
        organize_directory(directory)

    print("\nOrganização concluída!")

if __name__ == "__main__":
    main()
