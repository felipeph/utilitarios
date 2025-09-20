
import argparse
import os
import subprocess
import sys

def get_video_duration(filepath):
    """Usa ffprobe para obter a duração de um vídeo em segundos."""
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        filepath
    ]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout)
    except FileNotFoundError:
        print("Erro: 'ffprobe' não foi encontrado. Verifique se o FFmpeg está instalado e no PATH do sistema.", file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar ffprobe para o arquivo '{filepath}': {e.stderr}", file=sys.stderr)
        return None
    except ValueError:
        print(f"Não foi possível obter a duração do vídeo: '{filepath}'. O arquivo está corrompido ou não é um vídeo?", file=sys.stderr)
        return None

def extract_equally_spaced_frames(video_path, num_frames, base_output_dir):
    """
    Extrai uma quantidade de frames igualmente espaçados de um vídeo.
    """
    video_basename = os.path.splitext(os.path.basename(video_path))[0]
    print(f"\n--- Processando: {video_basename} ---")

    duration = get_video_duration(video_path)
    if duration is None:
        return

    # Cria o diretório de saída para os frames deste vídeo
    frame_output_dir = os.path.join(base_output_dir, f"{video_basename}_frames")
    try:
        os.makedirs(frame_output_dir, exist_ok=True)
    except OSError as e:
        print(f"Erro ao criar o diretório '{frame_output_dir}': {e}", file=sys.stderr)
        return

    print(f"Duração do vídeo: {duration:.2f} segundos. Extraindo {num_frames} frames.")
    print(f"Os frames serão salvos em: {frame_output_dir}")

    # Calcula o intervalo de tempo entre os frames
    # Usamos num_frames + 1 para espaçar os frames dentro do vídeo, não nas pontas
    interval = duration / (num_frames + 1)

    for i in range(1, num_frames + 1):
        timestamp = interval * i
        output_filename = os.path.join(frame_output_dir, f"frame_{i:02d}.jpg")
        
        print(f"  Extraindo frame {i}/{num_frames} no tempo {timestamp:.2f}s...")

        command = [
            'ffmpeg',
            '-y', # Sobrescreve o frame se já existir
            '-ss', str(timestamp), # Busca pelo tempo exato
            '-i', video_path,
            '-vframes', '1', # Extrai apenas 1 frame
            '-q:v', '2', # Qualidade do JPEG (1=melhor, 31=pior)
            output_filename
        ]

        try:
            # Escondemos a saída do ffmpeg para não poluir o terminal
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("Erro: 'ffmpeg' não foi encontrado. Verifique se o FFmpeg está instalado e no PATH do sistema.", file=sys.stderr)
            # Interrompe o loop se o ffmpeg não for encontrado
            return
        except subprocess.CalledProcessError as e:
            print(f"  Falha ao extrair frame no tempo {timestamp:.2f}s. Erro: {e.stderr}", file=sys.stderr)
    
    print(f"Extração de frames para '{video_basename}' concluída.")

def main():
    parser = argparse.ArgumentParser(
        description="Extrai N frames igualmente espaçados de arquivos de vídeo. Requer FFmpeg e ffprobe no PATH.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help="Caminho para o arquivo de vídeo ou para um arquivo .txt com uma lista de caminhos (um por linha)."
    )
    parser.add_argument(
        '-n', '--num-frames',
        type=int,
        default=10,
        help="Número de frames a serem extraídos de cada vídeo. Padrão: 10."
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='.',
        help="Diretório principal onde as pastas de frames serão criadas. Padrão: diretório atual."
    )

    args = parser.parse_args()

    # Valida o número de frames
    if args.num_frames <= 0:
        print("Erro: O número de frames deve ser maior que zero.", file=sys.stderr)
        sys.exit(1)

    video_files = []
    if args.input.lower().endswith('.txt'):
        print(f"Lendo lista de vídeos de: {args.input}")
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                for line in f:
                    filepath = line.strip()
                    if filepath and os.path.exists(filepath):
                        video_files.append(filepath)
                    elif filepath:
                        print(f"Aviso: Arquivo não encontrado na lista: '{filepath}'", file=sys.stderr)
        except FileNotFoundError:
            print(f"Erro: Arquivo de lista '{args.input}' não encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        if os.path.exists(args.input):
            video_files.append(args.input)
        else:
            print(f"Erro: Arquivo de vídeo '{args.input}' não encontrado.", file=sys.stderr)
            sys.exit(1)

    if not video_files:
        print("Nenhum arquivo de vídeo válido para processar.")
        sys.exit(0)

    print(f"Total de {len(video_files)} vídeo(s) para processar.")

    for video_path in video_files:
        extract_equally_spaced_frames(video_path, args.num_frames, args.output_dir)

if __name__ == "__main__":
    main()
