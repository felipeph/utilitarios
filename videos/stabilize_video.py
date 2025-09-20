
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

def stabilize_video(input_video, shakiness):
    """Estabiliza o vídeo."""
    output_video = os.path.splitext(input_video)[0] + '_stabilized.mp4'
    transforms_file = 'transforms.trf'

    if os.path.exists(output_video):
        if input(f"O vídeo estabilizado '{output_video}' já existe. Deseja recriá-lo? (s/n): ").lower() != 's':
            print("Usando o vídeo estabilizado existente.")
            return
        os.remove(output_video)

    command_detect = [
        'ffmpeg', '-i', input_video,
        '-vf', f'vidstabdetect=result={transforms_file}:shakiness={shakiness}',
        '-f', 'null', '-'
    ]
    run_ffmpeg_command(command_detect, f"Analisando tremor para estabilização em {input_video}")

    command_transform = [
        'ffmpeg', '-i', input_video,
        '-vf', f'vidstabtransform=input={transforms_file}:zoom=0:smoothing=10,unsharp=5:5:0.8:3:3:0.4',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-b:v', '20M',
        output_video
    ]
    run_ffmpeg_command(command_transform, f"Aplicando estabilização ({output_video})")

def main():
    parser = argparse.ArgumentParser(description="Estabiliza um vídeo.")
    parser.add_argument('--input', required=True, help='Caminho para o vídeo de entrada ou para um arquivo .txt com uma lista de vídeos.')
    parser.add_argument('--shakiness', type=int, default=5, help='Nível de agressividade da estabilização (1-10). Padrão: 5')
    args = parser.parse_args()

    if args.input.endswith('.txt'):
        with open(args.input, 'r') as f:
            videos = [line.strip() for line in f if line.strip()]
    else:
        videos = [args.input]

    for video in videos:
        try:
            stabilize_video(video, args.shakiness)
            print(f"\n--- Processo Finalizado para {video}! ---")
        except Exception as e:
            print(f"\nOcorreu um erro durante o processo de {video}: {e}")

if __name__ == '__main__':
    main()
