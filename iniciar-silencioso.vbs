' ===========================================================================
'  eye-rest-reminder — iniciar SEM abrir terminal (execução em segundo plano)
'
'  Dê DUPLO CLIQUE neste arquivo para iniciar o monitoramento sem nenhuma
'  janela. As notificações e o som de alerta continuam funcionando
'  normalmente. Como não há terminal, o log em tempo real NÃO fica visível.
'
'  Para PARAR o programa: abra o Gerenciador de Tarefas (Ctrl+Shift+Esc),
'  aba "Detalhes", e finalize o processo "pythonw.exe".
' ===========================================================================

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Roda a partir da pasta deste arquivo (portável — não depende de caminho fixo).
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = scriptDir

' Usa "pythonw.exe" resolvido pelo PATH do sistema (funciona em qualquer
' máquina onde o Python esteja instalado e no PATH). "pythonw" roda o Python
' sem abrir console.
' 0 = janela oculta ; False = não espera o processo terminar.
shell.Run "pythonw.exe main.py", 0, False
