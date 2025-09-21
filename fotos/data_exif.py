
import os
import argparse
import piexif
from datetime import datetime, timedelta

def edit_exif(folder_path, start_datetime_str, increment_seconds):
    """
    Edita a data e a hora EXIF das imagens em uma pasta.

    Args:
        folder_path (str): O caminho para a pasta que contém as imagens.
        start_datetime_str (str): A data e hora de início no formato 'YYYY-MM-DD HH:MM:SS'.
        increment_seconds (int): O número de segundos a incrementar para cada imagem.
    """
    try:
        start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print("Erro: Formato de data/hora inválido. Use 'YYYY-MM-DD HH:MM:SS'.")
        return

    try:
        files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.tiff'))])
    except FileNotFoundError:
        print(f"Erro: A pasta '{folder_path}' não foi encontrada.")
        return

    if not files:
        print(f"Nenhum arquivo de imagem encontrado em '{folder_path}'.")
        return

    current_datetime = start_datetime

    for filename in files:
        filepath = os.path.join(folder_path, filename)
        try:
            exif_dict = piexif.load(filepath)
            
            # Formata a string de data/hora para o EXIF
            exif_datetime_str = current_datetime.strftime('%Y:%m:%d %H:%M:%S')

            # Atualiza as tags EXIF
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_datetime_str.encode('utf-8')
            exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = exif_datetime_str.encode('utf-8')
            exif_dict['0th'][piexif.ImageIFD.DateTime] = exif_datetime_str.encode('utf-8')

            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, filepath)

            print(f"Atualizado {filename} para {exif_datetime_str}")

            # Incrementa a data/hora para a próxima imagem
            current_datetime += timedelta(seconds=increment_seconds)

        except Exception as e:
            print(f"Não foi possível processar {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Edita a data e a hora EXIF das imagens em uma pasta.")
    parser.add_argument("--folder", type=str, help="Caminho para a pasta com as imagens (padrão: pasta do script).")
    parser.add_argument("--datetime", type=str, required=True, help="Data e hora de início no formato 'YYYY-MM-DD HH:MM:SS'.")
    parser.add_argument("--increment", type=int, default=1, help="Incremento em segundos para cada imagem (padrão: 1).")

    args = parser.parse_args()

    folder = args.folder
    if folder is None:
        # Usa o diretório do script se nenhum for fornecido
        folder = os.path.dirname(os.path.realpath(__file__))

    edit_exif(folder, args.datetime, args.increment)
