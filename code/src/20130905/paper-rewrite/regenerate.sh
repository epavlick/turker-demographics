#!/bin/bash

#cat data/pass-1 | python scripts/googtrans-over-assigns.py > results/data/googmatch.assigns.txt
#python scripts/googtrans-over-turkers.py > results/data/googmatch.turkers.txt
#python scripts/googtrans-over-langs.py > results/data/googmatch.langs.txt

python scripts/quality-over-assigns-syns.py > results/data/quality.assigns.txt 
python scripts/quality-over-turkers-syns.py > results/data/quality.turkers.txt 
python scripts/quality-over-langs-syns.py > results/data/quality.langs.txt 

