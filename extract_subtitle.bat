@echo off

echo %*

if not exist "output/" mkdir "output/"

for %%A in (%*) do (
    ffmpeg.exe -i %%A -map 0:s:0 "output/%%~nA.srt"
)

pause