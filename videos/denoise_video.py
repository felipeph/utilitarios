
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

def denoise_video(input_video, strength):
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

    command = [
        'ffmpeg', '-i', input_video,
        '-vf', f'hqdn3d=luma_spatial={luma_spatial}:chroma_spatial={chroma_spatial}:luma_tmp={luma_tmp}:chroma_tmp={chroma_tmp}',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-b:v', '20M',
        output_video
    ]
    run_ffmpeg_command(command, f"Removendo ruído do vídeo ({output_video})")

def main():
    parser = argparse.ArgumentParser(description="Aplica redução de ruído em um vídeo.")
    parser.add_argument('--input', required=True, help='Caminho para o vídeo de entrada ou para um arquivo .txt com uma lista de vídeos.')
    parser.add_argument('--strength', type=int, default=4, help='Força da redução de ruído (1-10). Padrão: 4')
    args = parser.parse_args()

    if args.input.endswith('.txt'):
        with open(args.input, 'r') as f:
            videos = [line.strip() for line in f if line.strip()]
    else:
        videos = [args.input]

    for video in videos:
        try:
            denoise_video(video, args.strength)
            print(f"\n--- Processo Finalizado para {video}! ---")
        except Exception as e:
            print(f"\nOcorreu um erro durante o processo de {video}: {e}")

if __name__ == '__main__':
    main()
