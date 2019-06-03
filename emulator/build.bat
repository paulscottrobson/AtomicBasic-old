@echo off
copy ..\core\65816.? .
copy ..\core\65816core.c .
copy ..\core\traps.h .
rem
rem		Make the executabe
rem
mingw32-make


