import os
import sys
import subprocess
import argparse

def parse_time_to_seconds(time_str):
    """
    Converte uma string de tempo no formato 'MM:SS' ou apenas segundos para um total de segundos.
    """
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError("O formato de tempo deve ser MM:SS.")
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes * 60 + seconds
        else:
            return float(time_str)
    except (ValueError, TypeError) as e:
        print(f"ERRO: Formato de tempo inválido: '{time_str}'. Use 'MM:SS' ou segundos. Erro: {e}", file=sys.stderr)
        sys.exit(1)

def format_seconds_to_str(seconds):
    """
    Converte um total de segundos para uma string no formato 00m00s.
    """
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}m{secs:02d}s"

def get_video_duration(file_path):
    """Usa ffprobe para obter a duração do vídeo em segundos."""
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except FileNotFoundError:
        print("ERRO: O comando 'ffprobe' não foi encontrado.", file=sys.stderr)
        print("ffprobe faz parte do ffmpeg e é necessário para obter a duração do vídeo.", file=sys.stderr)
        sys.exit(1)
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"ERRO: Não foi possível obter a duração do vídeo '{file_path}'.", file=sys.stderr)
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

def split_video_segment(input_file, start_seconds, end_seconds):
    """
    Usa o ffmpeg para extrair um segmento de vídeo sem re-encoder.
    """
    base, ext = os.path.splitext(input_file)
    start_str = format_seconds_to_str(start_seconds)
    end_str = format_seconds_to_str(end_seconds)
    output_filename = f"{base}_split_{start_str}-{end_str}{ext}"

    if os.path.exists(output_filename):
        print(f"Arquivo de saída já existe, pulando: {output_filename}")
        return

    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', str(start_seconds),
        '-to', str(end_seconds),
        '-c', 'copy',  # Copia os streams sem re-encoder
        output_filename
    ]

    print(f"Criando segmento: {output_filename} (de {start_str} a {end_str})")
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao fatiar o vídeo para o segmento {start_str}-{end_str}.", file=sys.stderr)
        print(f"Comando: {' '.join(command)}", file=sys.stderr)
        print(f"Erro do ffmpeg: {e}", file=sys.stderr)
    except FileNotFoundError:
        print("ERRO: O comando 'ffmpeg' não foi encontrado.", file=sys.stderr)
        print("Por favor, instale o ffmpeg e garanta que ele esteja no PATH do seu sistema.", file=sys.stderr)
        sys.exit(1)

def main():
    """
    Função principal que analisa os argumentos e orquestra o fatiamento.
    """
    parser = argparse.ArgumentParser(
        description="Fatia um vídeo em múltiplos clipes baseado em uma sequência de tempos.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-f', '--file',
        required=True,
        help="Caminho para o arquivo de vídeo a ser fatiado."
    )
    parser.add_argument(
        '-t', '--timestamps',
        required=True,
        nargs='+',
        help="Sequência de tempos de corte. Ex: 1:15 2:30 5:00"
    )

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"ERRO: Arquivo de vídeo não encontrado em: {args.file}", file=sys.stderr)
        sys.exit(1)

    total_duration = get_video_duration(args.file)
    split_points_seconds = [parse_time_to_seconds(t) for t in args.timestamps]
    split_points_seconds.insert(0, 0)
    split_points_seconds = sorted(list(set(split_points_seconds)))

    # Adiciona a duração total do vídeo como o ponto de corte final, se necessário
    last_timestamp = split_points_seconds[-1]
    if last_timestamp < total_duration:
        # Evita criar clipes minúsculos no final
        if total_duration - last_timestamp > 1:
            split_points_seconds.append(total_duration)

    print(f"Fatiando o vídeo '{args.file}' (duração: {format_seconds_to_str(total_duration)}) nos tempos (s): {split_points_seconds}")

    # Itera sobre os pontos de corte para criar os segmentos
    for i in range(len(split_points_seconds) - 1):
        start_time = split_points_seconds[i]
        end_time = split_points_seconds[i+1]
        split_video_segment(args.file, start_time, end_time)
    
    print("\nProcesso de fatiamento concluído.")

if __name__ == '__main__':
    main()