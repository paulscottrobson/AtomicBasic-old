rm basic.dump  basic.bin basic.lst ../source/temp/*
pushd ../scripts
python gentokens.py
python basicblock.py
popd
cp ../scripts/temp/* ../source/temp
tass64 --m65816 -f -q ../source/start.asm -o basic.bin -L basic.lst
if [ -e basic.bin ]
then
../emulator/m65816 basic.bin
fi