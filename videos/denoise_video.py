import subprocess
import os
import argparse
import json

def get_video_bitrate(video_path):
    """Obtém o bitrate de um vídeo usando ffprobe."""
    command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        # Prioriza o bitrate do stream de vídeo, se disponível
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video' and 'bit_rate' in stream:
                return str(int(stream['bit_rate']))
        # Caso contrário, usa o bitrate do formato geral
        if 'format' in data and 'bit_rate' in data['format']:
            return str(int(data['format']['bit_rate']))
        return None
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao obter bitrate de {video_path}: {e}")
        return None

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

def denoise_video(input_video, strength, bitrate=None):
    """Aplica a redução de ruído."""
    output_video = os.path.splitext(input_video)[0] + '_denoised.mp4'

    if os.path.exists(output_video):
        if input(f"O vídeo com denoise '{output_video}' já existe. Deseja recriá-lo? (s/n): ").lower() != 's':
            print("Usando o vídeo com denoise existente.")
            return
        os.remove(output_video)

    # Mapeia a força para os parâmetros do hqdn3d
    luma_spatial = strength * 0.8
    chroma_spatial = strength * 0.6
    luma_tmp = strength * 1.2
    chroma_tmp = strength * 0.8

    # Define o bitrate
    if bitrate is None:
        print("Bitrate não especificado, tentando obter do vídeo original.")
        bitrate = get_video_bitrate(input_video)
        if bitrate:
            print(f"Bitrate do vídeo original: {bitrate} bps")
        else:
            print("Não foi possível obter o bitrate original. Usando padrão de 20M.")
            bitrate = '20M'

    command = [
        'ffmpeg', '-i', input_video,
        '-vf', f'hqdn3d=luma_spatial={luma_spatial}:chroma_spatial={chroma_spatial}:luma_tmp={luma_tmp}:chroma_tmp={chroma_tmp}',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-b:v', bitrate,
        output_video
    ]
    run_ffmpeg_command(command, f"Removendo ruído do vídeo ({output_video})")

def main():
    parser = argparse.ArgumentParser(description="Aplica redução de ruído em um vídeo.")
    parser.add_argument('--input', required=True, help='Caminho para o vídeo de entrada ou para um arquivo .txt com uma lista de vídeos.')
    parser.add_argument('--strength', type=int, default=4, help='Força da redução de ruído (1-10). Padrão: 4')
    parser.add_argument('--bitrate', help='Bitrate para o vídeo de saída (ex: 50M, 5000k). Se não especificado, usa o bitrate do vídeo original.')
    args = parser.parse_args()

    if args.input.endswith('.txt'):
        with open(args.input, 'r') as f:
            videos = [line.strip() for line in f if line.strip()]
    else:
        videos = [args.input]

    for video in videos:
        try:
            denoise_video(video, args.strength, args.bitrate)
            print(f"\n--- Processo Finalizado para {video}! ---")
        except Exception as e:
            print(f"\nOcorreu um erro durante o processo de {video}: {e}")

if __name__ == '__main__':
    main()
