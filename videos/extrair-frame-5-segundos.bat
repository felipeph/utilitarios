@echo off
setlocal

rem =================================================================
rem  Batch script to extract the first frame of all video files
rem  in the current directory using ffmpeg.
rem =================================================================

echo Iniciando o processo de extracao de frames...
echo.

rem Loop para cada tipo de arquivo de video na pasta atual.
rem Voce pode adicionar mais extensoes como *.webm, *.flv etc.
FOR %%F IN (*.mp4 *.mkv *.avi *.mov) DO (
    
    rem Verifica se o arquivo correspondente existe antes de processar
    if exist "%%F" (
        echo Processando arquivo: "%%F"
        
        rem "%%~nF" pega o nome do arquivo sem a extensao.
        rem O arquivo de saida sera algo como "meu_video.jpg".
        ffmpeg -ss 00:00:05 -i "%%F" -vframes 1 -y "%%~nF.jpg"
    )
)

echo.
echo Todos os videos foram processados.
pause
