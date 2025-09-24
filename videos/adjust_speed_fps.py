import os
import subprocess
import argparse
import sys

# Lista de extensões de vídeo a serem processadas.
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv')

def get_atempo_filter(speed):
    """
    Cria a string de filtro 'atempo' para o ffmpeg, lidando com a limitação de 0.5.
    O filtro atempo só aceita valores entre 0.5 e 100.0. Para desacelerar mais,
    é preciso encadear o filtro (ex: atempo=0.5,atempo=0.8 para 0.4).
    """
    tempo = 1.0 / speed
    if tempo >= 0.5:
        return f"atempo={tempo}"
    
    filters = []
    while tempo < 0.5:
        filters.append("atempo=0.5")
        tempo /= 0.5
    
    filters.append(f"atempo={tempo}")
    return ",".join(filters)

def process_video_file(input_path, output_path, speed, fps, audio_mode):
    """
    Executa o comando ffmpeg para aplicar o efeito de slow motion em um único arquivo de vídeo.
    """
    if os.path.exists(output_path):
        print(f"Arquivo de saída já existe, pulando: {os.path.basename(output_path)}")
        return

    print(f"Processando: {os.path.basename(input_path)}")

    command = [
        'ffmpeg',
        '-i', input_path,
        '-filter:v', f'setpts={speed}*PTS',
        '-r', str(fps),
        '-b:v', '35M',
    ]

    if audio_mode == 'remove':
        command.append('-an')
    elif audio_mode == 'slow':
        atempo_filter = get_atempo_filter(speed)
        command.extend(['-af', atempo_filter])

    command.append(output_path)

    try:
        # Usamos DEVNULL para não poluir a saída do script com o output do ffmpeg
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Concluído: {os.path.basename(output_path)}")
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao processar {os.path.basename(input_path)}.", file=sys.stderr)
        print(f"Comando: {' '.join(command)}", file=sys.stderr)
        print(f"Erro do ffmpeg: {e}", file=sys.stderr)
    except FileNotFoundError:
        print("ERRO: O comando 'ffmpeg' não foi encontrado.", file=sys.stderr)
        print("Por favor, instale o ffmpeg e garanta que ele esteja no PATH do seu sistema.", file=sys.stderr)
        sys.exit(1)


def process_folder(folder_path, speed, fps, audio_mode):
    """
    Varre uma pasta em busca de arquivos de vídeo e os processa, salvando em uma subpasta.
    """
    # Montar o nome da subpasta de saída
    audio_str = "no-audio" if audio_mode == 'remove' else "slow-audio"
    output_folder_name = f"slow_{speed}x_{fps}fps_{audio_str}"
    output_dir = os.path.join(folder_path, output_folder_name)

    # Criar a pasta de saída se ela não existir
    os.makedirs(output_dir, exist_ok=True)

    print(f"--- Iniciando processamento da pasta: {folder_path} ---")
    print(f"--- Saída será salva em: {output_dir} ---")
    
    found_videos = False
    for filename in os.listdir(folder_path):
        # Ignorar a própria pasta de saída para não processar o que já foi processado
        if os.path.isdir(os.path.join(folder_path, filename)) and filename == output_folder_name:
            continue

        if filename.lower().endswith(VIDEO_EXTENSIONS):
            found_videos = True
            base, ext = os.path.splitext(filename)
            
            # Evita reprocessar arquivos que já parecem ter sido processados
            if f'_slow_{speed}x' in base:
                print(f"Arquivo já parece processado, pulando: {filename}")
                continue

            input_file_path = os.path.join(folder_path, filename)
            # Usar o novo diretório para o arquivo de saída
            output_file_path = os.path.join(output_dir, f"{base}_slow_{speed}x{ext}")
            
            process_video_file(input_file_path, output_file_path, speed, fps, audio_mode)

    if not found_videos:
        print("Nenhum arquivo de vídeo encontrado na pasta.")
    print(f"--- Processamento da pasta finalizado: {folder_path} ---")
    print()


def main():
    """
    Função principal que analisa os argumentos da linha de comando.
    """
    parser = argparse.ArgumentParser(
        description="Processa vídeos com ffmpeg para criar um efeito de slow motion.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--folder',
        type=str,
        help="Caminho para a pasta contendo os vídeos. Padrão: pasta atual."
    )
    group.add_argument(
        '--file',
        type=str,
        help="Caminho para um arquivo .txt contendo uma lista de pastas (uma por linha)."
    )

    parser.add_argument(
        '--speed',
        type=float,
        required=True,
        help="Multiplicador de velocidade (e.g., 2.5 para 2.5x mais lento). OBRIGATÓRIO."
    )
    parser.add_argument(
        '--fps',
        type=int,
        required=True,
        help="Framerate de destino do vídeo final. OBRIGATÓRIO."
    )
    parser.add_argument(
        '--audio',
        type=str,
        choices=['remove', 'slow'],
        default='remove',
        help="Modo de áudio: 'remove' para tirar o áudio, 'slow' para desacelerar. Padrão: remove."
    )

    args = parser.parse_args()

    if args.folder:
        if not os.path.isdir(args.folder):
            print(f"ERRO: A pasta especificada não existe: {args.folder}", file=sys.stderr)
            sys.exit(1)
        process_folder(args.folder, args.speed, args.fps, args.audio)
    elif args.file:
        if not os.path.isfile(args.file):
            print(f"ERRO: O arquivo especificado não existe: {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, 'r', encoding='utf-8') as f:
            folders = [line.strip() for line in f if line.strip()]
            for folder in folders:
                if os.path.isdir(folder):
                    process_folder(folder, args.speed, args.fps, args.audio)
                else:
                    print(f"AVISO: A pasta listada no arquivo não foi encontrada: {folder}")
    else:
        current_directory = os.getcwd()
        print(f"Nenhum caminho fornecido. Usando o diretório de trabalho atual: {current_directory}")
        process_folder(current_directory, args.speed, args.fps, args.audio)

if __name__ == '__main__':
    main()