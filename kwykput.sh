#!/bin/bash
# kwykput.sh: a script to convert the output of kwyk into regional volumes
# Usage: kwykput.sh kwyk_output_file results_file
kwyk_output_file=$1
output=$2
kwyk_index=~/kwyk/kwyk_region_index.csv
 
if [ -z $output ]; then
	echo "you must provide an output filename, buy..."
	exit
fi

# say hello
echo ""
echo "Doing the kwyk volume calculation on $kwyk_output_file"

# check for kwyk-file existance
if [ -f "$kwyk_output_file" ]; then
    echo "$kwyk_output_file exists, yay, we continue"
else 
    echo "$kwyk_output_file does not exist, boo, we must quit..."
    echo ""
    exit
fi

# check for kwyk-region-index file existance
if [ -f "$kwyk_index" ]; then
    echo "$kwyk_index exists, yay, we continue"
else 
    echo "$kwyk_index does not exist, boo, we must quit..."
    echo ""
    exit
fi


# prepare output file
# check if already exists (don't overwrite...)
if [ -f "$output" ]; then
    echo "$output exists, we will do no harm, and must exit..."
    exit
fi

# header line in output
echo "kywk_index label number_voxels vol_inmm3" >> $output

# loop for the kwyk fill values
OLDIFS=$IFS
IFS=,
while read index label
do
	echo "    Doing: index = $index, label = $label"
	if [[ $index != "0" && $index != "kwyk_index" ]]; then 
		let lindex=$index-1
		let uindex=$index+1
		echo -n "$index $label " >> $output
		fslstats $kwyk_output_file -l $lindex -u $uindex -V >> $output
	fi
done < $kwyk_index
IFS=$OLDIF
echo ""

# the end
echo "we have come to the end, goodbye!"
exit


