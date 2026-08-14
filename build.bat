@echo off
REM Gera o eye-rest-reminder.exe (arquivo unico) com o PyInstaller.
REM Duplo-clique ou rode no terminal. A saida fica em dist\eye-rest-reminder.exe
setlocal

echo === Instalando dependencias de build (pyinstaller) ===
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt

echo.
echo === Limpando builds anteriores ===
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo === Compilando (isso pode demorar alguns minutos) ===
python -m PyInstaller eye-rest-reminder.spec --noconfirm

echo.
if exist dist\eye-rest-reminder.exe (
    echo === PRONTO! O executavel esta em: dist\eye-rest-reminder.exe ===
) else (
    echo === FALHOU: o executavel nao foi gerado. Veja os erros acima. ===
)
endlocal
