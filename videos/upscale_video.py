
import subprocess
import os
import argparse

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

def upscale_video(input_video, resolution, bitrate):
    """Faz o upscale do vídeo."""
    output_video = os.path.splitext(input_video)[0] + f'_upscaled_{resolution.replace(":", "x")}.mp4'

    if os.path.exists(output_video):
        if input(f"O vídeo final em {resolution} '{output_video}' já existe. Deseja recriá-lo? (s/n): ").lower() != 's':
            print(f"Usando o vídeo {resolution} existente.")
            return
        os.remove(output_video)

    command = [
        'ffmpeg', '-i', input_video,
        '-vf', f'scale={resolution}:flags=lanczos',
        '-c:v', 'libx264', '-preset', 'slow', '-b:v', bitrate,
        '-pix_fmt', 'yuv420p', output_video
    ]
    run_ffmpeg_command(command, f"Convertendo para {resolution} ({output_video})")

def main():
    parser = argparse.ArgumentParser(description="Faz o upscale de um vídeo.")
    parser.add_argument('--input', required=True, help='Caminho para o vídeo de entrada.')
    parser.add_argument('--resolution', type=str, default='3840:2160', help='Resolução de saída (ex: 3840:2160 para 4K). Padrão: 3840:2160')
    parser.add_argument('--bitrate', type=str, default='60M', help='Bitrate do vídeo (ex: 60M). Padrão: 60M')
    args = parser.parse_args()

    try:
        upscale_video(args.input, args.resolution, args.bitrate)
        print(f"\n--- Processo Finalizado! ---")
    except Exception as e:
        print(f"\nOcorreu um erro durante o processo: {e}")

if __name__ == '__main__':
    main()
