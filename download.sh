#!/bin/bash

# This file downloads all of the files (.cat, .hea, ...) from the physionet database into
# the current working directory.

# Constants:
MAX_FIRST_NUM=2
MAX_LAST_NUMS=( 24 34 )

# First loop over all possible first digits in the file name.
FIRST_NUM=1
while [ $FIRST_NUM -le $MAX_FIRST_NUM ];
do
	INDEX=$((FIRST_NUM-1))	
	
	# Determine the maximum value of the latter two digits
	# in the file name, given the first digit in the file name.
	MAX_LAST_NUM=${MAX_LAST_NUMS[$INDEX]}

	#if [ $FIRST_NUM -eq 1  ]
	#then
	#	MAX_LAST_NUM=24
	#else
	#	MAX_LAST_NUM=34
	#fi

	# Loop over all possible file names.
	LAST_NUM=0
	while [ $LAST_NUM -le $MAX_LAST_NUM ];
	do
		NUM=$((100*FIRST_NUM+LAST_NUM))

		BEG_FILENAME="https://www.physionet.org/physiobank/database/mitdb/"$NUM		
		# Loop over all possible extensions.
		COUNT=0
		while [ $COUNT -le 2 ]; do
			EXTENSION=""

			if [ $COUNT -eq 0 ]
			then
				EXTENSION=".atr"
			elif [ $COUNT -eq 1 ]
			then
				EXTENSION=".dat"
			else
				EXTENSION=".hea"
			fi
			
			FILENAME=$BEG_FILENAME$EXTENSION
			wget $FILENAME 				

			COUNT=$(($COUNT+1))
		done		
		

		LAST_NUM=$(($LAST_NUM+1)) 
	done

        FIRST_NUM=$(($FIRST_NUM+1))

done
