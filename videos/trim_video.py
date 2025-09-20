
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

def trim_video(video_path, start_trim, end_trim, suffix):
    """
    Corta um vídeo usando ffmpeg sem re-renderizar.
    """
    print(f"\n--- Processando: {os.path.basename(video_path)} ---")

    original_duration = get_video_duration(video_path)
    if original_duration is None:
        return # Pula para o próximo arquivo se a duração não puder ser obtida

    new_duration = original_duration - start_trim - end_trim

    if new_duration <= 0:
        print(f"Erro: O tempo de corte ({start_trim + end_trim:.2f}s) é maior ou igual à duração do vídeo ({original_duration:.2f}s).")
        print("O vídeo não foi modificado.")
        return

    # Constrói o nome do arquivo de saída
    base, ext = os.path.splitext(video_path)
    output_path = f"{base}{suffix}{ext}"

    # Comando ffmpeg para corte rápido
    command = [
        'ffmpeg',
        '-y',  # Sobrescreve o arquivo de saída se ele já existir
        '-ss', str(start_trim),
        '-i', video_path,
        '-t', str(new_duration),
        '-c', 'copy', # Copia os codecs de áudio e vídeo sem re-renderizar
        output_path
    ]

    print(f"Duração original: {original_duration:.2f} segundos")
    print(f"Cortando {start_trim:.2f}s do início e {end_trim:.2f}s do fim.")
    print(f"Nova duração estimada: {new_duration:.2f} segundos")
    print("Executando ffmpeg...")

    try:
        # Usamos Popen para poder mostrar a saída do ffmpeg em tempo real se quisermos,
        # mas por enquanto vamos apenas esperar a conclusão.
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Erro ao executar ffmpeg: {stderr.decode('utf-8')}", file=sys.stderr)
        else:
            final_duration = get_video_duration(output_path)
            print(f"Sucesso! Vídeo salvo em: {os.path.basename(output_path)}")
            if final_duration:
                print(f"Duração final confirmada: {final_duration:.2f} segundos")

    except FileNotFoundError:
        print("Erro: 'ffmpeg' não foi encontrado. Verifique se o FFmpeg está instalado e no PATH do sistema.", file=sys.stderr)
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Corta vídeos usando FFmpeg sem re-renderizar. Requer FFmpeg e ffprobe no PATH do sistema.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help="Caminho para o arquivo de vídeo ou para um arquivo .txt contendo uma lista de caminhos de vídeo (um por linha)."
    )
    parser.add_argument(
        '-s', '--start',
        type=float,
        default=0.0,
        help="Segundos a serem removidos do INÍCIO do vídeo. Ex: 0.5"
    )
    parser.add_argument(
        '-e', '--end',
        type=float,
        default=0.0,
        help="Segundos a serem removidos do FIM do vídeo. Ex: 1.2"
    )
    parser.add_argument(
        '--suffix',
        type=str,
        default='_cortado',
        help="Sufixo a ser adicionado ao nome do arquivo de saída. Padrão: '_cortado'"
    )

    args = parser.parse_args()

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
        trim_video(video_path, args.start, args.end, args.suffix)

if __name__ == "__main__":
    main()
