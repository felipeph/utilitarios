
import os
import datetime
import re
import argparse
from PIL import Image
from PIL.ExifTags import TAGS
from tinytag import TinyTag

import cv2

# --- Configurações ---
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.heic', '.tiff')
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv', '.3gp')
EXIF_DATETIME_TAG = 36867

def get_exif_datetime(file_path):
    """Extrai a data e hora 'DateTimeOriginal' de um arquivo de imagem."""
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data and EXIF_DATETIME_TAG in exif_data:
                date_str = exif_data[EXIF_DATETIME_TAG]
                return datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except Exception:
        pass
    return None

def get_camera_model(file_path):
    """Extrai e sanitiza o modelo da câmera dos dados EXIF."""
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data:
                make = exif_data.get(271, '')  # Make
                model = exif_data.get(272, '') # Model
                camera_name = f"{make.strip()} {model.strip()}".strip()
                if camera_name:
                    return re.sub(r'[^\w_.-]', '_', camera_name).replace('__', '_')
    except Exception:
        pass
    return None

def get_video_info(file_path):
    """Extrai framerate, resolução e modelo da câmera de um arquivo de vídeo."""
    video_info_str = None
    camera_model = None
    try:
        # Usa OpenCV para info de vídeo
        cap = cv2.VideoCapture(file_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            if fps > 0 and width > 0 and height > 0:
                video_info_str = f"{round(fps)}fps_{width}x{height}"

        # Usa TinyTag para metadados adicionais (tentar obter a câmera)
        tag = TinyTag.get(file_path)
        if tag and tag.artist:
             camera_model = re.sub(r'[^\w_.-]', '_', tag.artist).replace('__', '_')

    except Exception:
        pass
    return video_info_str, camera_model

def get_file_modification_datetime(file_path):
    """Obtém a data e hora da última modificação de um arquivo."""
    try:
        mtime = os.path.getmtime(file_path)
        return datetime.datetime.fromtimestamp(mtime)
    except Exception as e:
        print(f"  [Erro] Não foi possível ler a data de modificação de {os.path.basename(file_path)}: {e}")
        return None

def sanitize_folder_name(folder_name):
    """Remove a data inicial (YYYY-MM-DD) e formata o nome do evento."""
    name_without_date = re.sub(r'^\d{4}-\d{2}-\d{2}[-_]?', '', folder_name)
    sanitized = re.sub(r'[\s-]+', '_', name_without_date)
    sanitized = re.sub(r'[^\w_]', '', sanitized)
    return sanitized.strip('_')

def process_directory(root_path):
    """Vasculha um único diretório e renomeia os arquivos de mídia."""
    print(f"--- Processando diretório: {root_path} ---")
    total_renamed_in_dir = 0
    
    for dirpath, _, filenames in os.walk(root_path):
        if not filenames:
            continue

        folder_name = os.path.basename(dirpath)
        event_name = sanitize_folder_name(folder_name)
        
        if not event_name:
            if dirpath == root_path:
                continue
            event_name = sanitize_folder_name(os.path.basename(root_path))

        for filename in filenames:
            file_ext = os.path.splitext(filename)[1].lower()
            full_path = os.path.join(dirpath, filename)
            
            timestamp = None
            camera_model = None
            video_info = None

            if file_ext in IMAGE_EXTENSIONS:
                timestamp = get_exif_datetime(full_path)
                camera_model = get_camera_model(full_path)
                if not timestamp:
                    timestamp = get_file_modification_datetime(full_path)
            elif file_ext in VIDEO_EXTENSIONS:
                timestamp = get_file_modification_datetime(full_path)
                video_info, camera_model = get_video_info(full_path)
            else:
                continue

            if not timestamp:
                print(f"  [Aviso] Não foi possível obter data para: {filename}. Pulando.")
                continue

            date_str = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
            
            base_new_name = f"{date_str}_{event_name}"
            if camera_model:
                base_new_name += f"_{camera_model}"
            if video_info:
                base_new_name += f"_{video_info}"

            counter = 0
            while True:
                new_filename = f"{base_new_name}_{counter:02d}{file_ext}"
                new_full_path = os.path.join(dirpath, new_filename)
                if not os.path.exists(new_full_path):
                    break
                counter += 1

            if full_path == new_full_path:
                continue
            
            try:
                os.rename(full_path, new_full_path)
                print(f"  -> Renomeado: {filename} >> {new_filename}")
                total_renamed_in_dir += 1
            except OSError as e:
                print(f"  [Erro] Falha ao renomear {filename}: {e}")
    
    print(f"--- Concluído para {root_path}. {total_renamed_in_dir} arquivos renomeados. ---")
    print()
    return total_renamed_in_dir

def process_from_file_list(file_list_path):
    """Lê uma lista de diretórios de um arquivo de texto e processa cada um."""
    print(f"Modo de lista de arquivo detectado. Lendo: {file_list_path}")
    print()
    try:
        with open(file_list_path, 'r', encoding='utf-8') as f:
            paths_to_process = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[Erro] O arquivo de lista '{file_list_path}' não foi encontrado.")
        return
    except Exception as e:
        print(f"[Erro] Não foi possível ler o arquivo '{file_list_path}': {e}")
        return

    if not paths_to_process:
        print("[Aviso] O arquivo de lista está vazio. Nenhum diretório para processar.")
        return

    print(f"Encontrados {len(paths_to_process)} diretórios para processar.")
    grand_total_renamed = 0

    for path in paths_to_process:
        if os.path.isdir(path):
            grand_total_renamed += process_directory(path)
        else:
            print(f"--- [Aviso] Ignorando linha, pois não é um diretório válido: '{path}' ---")
            print()
    
    print()
    print(f"Processo finalizado! Total geral de {grand_total_renamed} arquivos renomeados em todos os diretórios.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Renomeia arquivos de mídia em um diretório específico ou em múltiplos diretórios listados em um arquivo de texto.",
        epilog="Forneça um caminho para um diretório ou para um arquivo .txt contendo uma lista de diretórios."
    )
    parser.add_argument(
        "input_path",
        help="O caminho para um único diretório a ser processado OU para um arquivo .txt contendo a lista de diretórios."
    )
    args = parser.parse_args()

    target_path = args.input_path

    if os.path.isdir(target_path):
        # O caminho é um diretório, processa-o diretamente.
        print("Modo de diretório único detectado.")
        process_directory(target_path)
    elif os.path.isfile(target_path):
        # O caminho é um arquivo, processa como uma lista.
        process_from_file_list(target_path)
    else:
        print(f"[Erro] O caminho fornecido não é um diretório ou arquivo válido: {target_path}")
