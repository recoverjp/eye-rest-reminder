@echo off
REM ==========================================================================
REM  eye-rest-reminder — iniciar COM a janela de log visivel.
REM
REM  De duplo clique neste arquivo para iniciar o monitoramento. Uma janela
REM  de terminal abre mostrando o log em tempo real (rosto detectado, tempo
REM  continuo, etc). Para PARAR, feche a janela ou pressione Ctrl+C.
REM
REM  Se voce quer rodar SEM nenhuma janela, use "iniciar-silencioso.vbs".
REM ==========================================================================

REM Vai para a pasta onde este .bat esta, independente de onde foi chamado.
cd /d "%~dp0"

title eye-rest-reminder
python main.py

REM Se o programa terminar por erro, mantem a janela aberta para ler a mensagem.
echo.
echo --- Programa encerrado. Pressione uma tecla para fechar. ---
pause >nul
