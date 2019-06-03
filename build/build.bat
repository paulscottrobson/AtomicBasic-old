@echo off
del /Q basic.dump 
del /Q basic.bin 
del /Q basic.lst 
del /Q ..\source\temp\*
pushd ..\scripts
python gentokens.py
python basicblock.py
popd
copy ..\scripts\temp\* ..\source\temp
64tass --m65816 -f -q ..\source\start.asm -o basic.bin -L basic.lst
if errorlevel 1 goto exit
..\emulator\m65816 basic.bin
:exit
