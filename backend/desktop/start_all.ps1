$python = "D:\Documents\playlist\backend\venv\Scripts\python.exe"
$desktop = "D:\Documents\playlist\backend\desktop"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$desktop'; & '$python' p1_watcher.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$desktop'; & '$python' p2_extractor.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$desktop'; & '$python' p3_sender.py"

Write-Host "P1, P2, P3 démarrés dans 3 fenêtres séparées."
