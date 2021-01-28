Awk command to find derivative of Moon scan to get approximate beam

 awk -F, 'NR-1{print $3,$8,$8-p}{p=$8}' moonScan.txt > moonScanDiff.txt
