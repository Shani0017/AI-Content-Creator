' Starts AI Content Creator without a black console window.
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
here = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = here
If Not fso.FileExists(here & "\.venv\Scripts\pythonw.exe") Then
  ' first run: set everything up (shows the setup window once)
  sh.Run "cmd /c """ & here & "\setup.bat""", 1, True
End If
sh.Run """" & here & "\.venv\Scripts\pythonw.exe"" """ & here & "\app.py""", 0, False
