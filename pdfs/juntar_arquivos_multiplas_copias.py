#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script interativo para juntar múltiplos arquivos PDF em um único arquivo,
utilizando argumentos de linha de comando para especificar os arquivos e o número de cópias.
"""

import argparse
import sys

try:
    from pypdf import PdfWriter, PdfReader
except ImportError:
    print("ERRO: A biblioteca pypdf não está instalada.")
    print("Por favor, instale-a executando o seguinte comando no seu terminal:")
    print("pip install pypdf")
    sys.exit(1)

def create_arg_parser():
    """Cria e configura o parser de argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Junta vários arquivos PDF em um, com um número específico de cópias para cada um.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Exemplo de uso:\n  python %(prog)s modelo_A.pdf 10 modelo_B.pdf 15 -o provas_finais.pdf"
    )
    parser.add_argument(
        "pdf_args",
        metavar="<arquivo.pdf> <n_copias>",
        nargs="*",
        help="Pares de nome de arquivo PDF seguido pelo número de cópias desejado."
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_filename",
        default="provas_combinadas.pdf",
        help="Nome do arquivo PDF de saída. (Padrão: %(default)s)"
    )
    return parser

def parse_pdf_input_args(args):
    """Valida e processa os argumentos de entrada em um dicionário de arquivos e cópias."""
    if not args:
        return None
    if len(args) % 2 != 0:
        print(f"ERRO: Número ímpar de argumentos ({len(args)}). Os argumentos devem ser em pares: <arquivo.pdf> <n_copias>.")
        sys.exit(1)

    pdf_files_to_merge = {}
    for i in range(0, len(args), 2):
        filename = args[i]
        try:
            num_copies = int(args[i+1])
            if num_copies <= 0:
                raise ValueError("O número de cópias deve ser positivo.")
            pdf_files_to_merge[filename] = num_copies
        except ValueError:
            print(f"ERRO: O número de cópias '{args[i+1]}' para o arquivo '{filename}' é inválido. Deve ser um número inteiro maior que zero.")
            sys.exit(1)
    return pdf_files_to_merge

def merge_pdfs(pdfs_to_merge, output_filename):
    """Lê, copia e junta os PDFs em um único arquivo de saída."""
    merger = PdfWriter()
    print("Iniciando a criação do PDF combinado...")

    for filename, num_copies in pdfs_to_merge.items():
        try:
            print(f"Processando: '{filename}'...")
            with open(filename, "rb") as f:
                reader = PdfReader(f)
                for i in range(num_copies):
                    merger.append(reader)
                    print(f"  - Cópia {i+1}/{num_copies} de '{filename}' adicionada.")
            print(f"'{filename}' processado com sucesso.")
        except FileNotFoundError:
            print(f"\nERRO CRÍTICO: O arquivo de entrada '{filename}' não foi encontrado.")
            print("Verifique o nome e o caminho do arquivo e tente novamente.")
            return
        except Exception as e:
            print(f"\nOcorreu um erro inesperado ao processar '{filename}': {e}")
            return

    try:
        print(f"\nSalvando o arquivo final como '{output_filename}'...")
        with open(output_filename, "wb") as f_out:
            merger.write(f_out)
        
        total_files = len(pdfs_to_merge)
        total_copies = sum(pdfs_to_merge.values())
        print("\n--------------------------------------------------")
        print("  PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"  O arquivo '{output_filename}' foi criado.")
        print(f"  Contém {total_copies} provas de {total_files} modelo(s) diferente(s).")
        print("--------------------------------------------------")
    except Exception as e:
        print(f"\nOcorreu um erro ao salvar o arquivo final: {e}")

def main():
    """Função principal para orquestrar a execução do script."""
    arg_parser = create_arg_parser()
    cli_args = arg_parser.parse_args()

    pdfs_to_merge = parse_pdf_input_args(cli_args.pdf_args)

    if not pdfs_to_merge:
        arg_parser.print_help()
        return

    merge_pdfs(pdfs_to_merge, cli_args.output_filename)

if __name__ == "__main__":
    main()
