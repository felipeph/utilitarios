import subprocess
import os
import glob
import argparse
import re

def run_ffmpeg_command(command, description):
    """Executa um comando ffmpeg e imprime o status."""
    print(f"--- {description} ---")
    print(f"Executando comando: {' '.join(command)}")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', errors='replace')
        for line in process.stdout:
            print(line, end='')
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)
        print(f"Sucesso: {description} concluído.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao executar o comando: {' '.join(command)}")
        raise
    print("-" * (len(description) + 6) + "\n")

def create_base_video(bitrate, folder, output_filename):
    """Cria o vídeo base a partir da sequência de imagens."""
    if os.path.exists(output_filename):
        if input(f"O arquivo de vídeo base '{output_filename}' já existe. Deseja recriá-lo? (s/n): ").lower() != 's':
            print("Usando o vídeo base existente.")
            return
        os.remove(output_filename)

    image_pattern = os.path.join(folder, '*.JPG')
    print(f"Procurando por arquivos de imagem com o padrão: {image_pattern}")
    image_files = sorted(glob.glob(image_pattern))

    if not image_files:
        print(f"ERRO: Nenhum arquivo de imagem encontrado com o padrão '{image_pattern}'")
        raise FileNotFoundError(f"Nenhum arquivo JPG encontrado no diretório.")

    print(f"{len(image_files)} arquivos de imagem.")

    list_filename = "filelist.txt"
    with open(list_filename, "w") as f:
        for image_file in image_files:
            f.write(f"file '{os.path.abspath(image_file).replace(\",'/')}'\n")

    command = [
        'ffmpeg', '-r', '30', '-f', 'concat', '-safe', '0', '-i', list_filename,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-b:v', bitrate, output_filename
    ]
    
    try:
        run_ffmpeg_command(command, f"Criando vídeo base ({output_filename})")
    finally:
        if os.path.exists(list_filename):
            os.remove(list_filename)
            print(f"Arquivo temporário '{list_filename}' removido.")

def simplify_filename(name):
    """Simplifica o nome do arquivo removendo espaços e caracteres especiais."""
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[^0-9a-zA-Z_.-]', '', name)
    return name

def main():
    parser = argparse.ArgumentParser(description="Cria um timelapse a partir de uma pasta de imagens.")
    parser.add_argument('--bitrate', type=str, default='20M', help='Bitrate do vídeo (ex: 20M, 50M). Padrão: 20M')
    parser.add_argument('--folder', type=str, default='.', help='Pasta contendo as imagens. Padrão: pasta atual')
    args = parser.parse_args()

    folder_name = os.path.basename(os.path.abspath(args.folder))
    output_filename = simplify_filename(folder_name) + ".mp4"

    try:
        create_base_video(args.bitrate, args.folder, output_filename)
        print(f"\n--- Processo Finalizado! ---")
        print(f"Seu vídeo de timelapse está pronto: '{output_filename}'")
    except Exception as e:
        print(f"\nOcorreu um erro durante o processo: {e}")

if __name__ == '__main__':
    main()