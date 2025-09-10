@echo off
echo Criando a lista de arquivos...
(for %%i in (*.mp4) do @echo file '%%i') > lista.txt

echo Juntando os videos com FFmpeg...
ffmpeg -f concat -safe 0 -i lista.txt -c copy video_final.mp4

echo Limpando arquivos temporarios...
del lista.txt

echo Processo concluido! O video final esta salvo como "video_final.mp4".
pause
