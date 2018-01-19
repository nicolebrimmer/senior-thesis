#!/usr/bin/env python

from readData import CARDIAC_EVENTS, getData
from LSTM import runModel
from prepareForLSTM import divideIntoTrainingAndTesting, convertIntoNumpyArrays

import random
import pickle
import numpy as np
import os.path
import os

np.random.seed(1337)  # for reproducibility

# ************************************************************
# OPEN TWO FILES
# ************************************************************
overviewFileName = '../results/resultsOverview.txt'
verboseFileName = '../results/resultsVerbose.txt'

# If these files already exist then delete them.
if (os.path.isfile(overviewFileName)):
	os.remove(overviewFileName)
if (os.path.isfile(verboseFileName)):
	os.remove(verboseFileName)

# Create the files.
overviewFile = open(overviewFileName, 'w')
verboseFile = open(verboseFileName, 'w')

# ***********************************************************
# SET UP LIST OF VALUES
# ***********************************************************

#timeBefores = np.array([0.0])
#timeWindows = np.array([2.0])
timeBefores = np.linspace(0, 20, 5)
timeWindows = np.linspace(2, 22, 5)

numOfTimeBefores = timeBefores.shape[0]
numOfTimeWindows = timeWindows.shape[0]

sensitivities = np.empty((numOfTimeBefores, numOfTimeWindows), dtype = float)
specificities = np.empty((numOfTimeBefores, numOfTimeWindows), dtype = float)

count = 0
total = numOfTimeBefores * numOfTimeWindows

for timeBeforeIndex in range(numOfTimeBefores):
	amountOfTimeBeforeBeg = timeBefores[timeBeforeIndex]

	for timeWindowIndex in range(numOfTimeWindows):
		timeWindow = timeWindows[timeWindowIndex]
		
		count = count + 1		
		print ('*********************************************')
		print ('Doing set of ' + str(count) + ' \ ' + str(total))
		print ('*********************************************')

		verboseFile.write('**************************************************************\n')
		verboseFile.write('Amount of time before beginning: ' + str(amountOfTimeBeforeBeg) + '\n')
		verboseFile.write('Time Window: ' + str(timeWindow) + '\n')
		verboseFile.write('**************************************************************\n\n')

		# ************************************************************
		# EXTRACTION OF ECG SIGNALS FROM DATABASES
		# ************************************************************
		print 'Extracting ECG signals from the databases... '

		# Get the [Beats] objects that are [timeWindow] seconds in length
		# and that end [amountOfTimeBeforeBeg] seconds before an abnormal
		# cardiac rhythm begins.
		fileName = '../listOfBeatsObjs/listOfBeatsObjs' + str(amountOfTimeBeforeBeg) + '-' + str(timeWindow)
		fileExists = os.path.isfile(fileName)
		#if (True):
		if (not(fileExists)):
			doCreateTextFiles = False
			listOfBeatsObjs = getData(amountOfTimeBeforeBeg, timeWindow, doCreateTextFiles)
			with open(fileName, 'w') as f:
		    		pickle.dump([listOfBeatsObjs], f)
		else:
			with open(fileName) as f:
		    		listOfBeatsObjs = pickle.load(f)[0]
		
		print 'Completed! \n'

		# ********************************************************
		# DIVISION OF ECG SIGNALS INTO TRAINING AND TESTING DATA
		# *******************************************************
		print 'Dividing the ECG signals into training and testing data...'
		# The fraction of the [Beats] objects that should be a part of the
		# training data.
		trainingFract = 0.5
		(trainingObjs, testingObjs) = divideIntoTrainingAndTesting(listOfBeatsObjs, trainingFract)
		print 'Completed! \n'

		# *********************************************************
		# CONVERT INTO NUMPY ARRAYS
		# ********************************************************
		print 'Converting ECG signals into numpy arrays...'
		(trainingX, trainingY, testingX, testingY) = convertIntoNumpyArrays(listOfBeatsObjs, trainingObjs, testingObjs)
		print 'Completed! \n'

		# *********************************************************
		# CREATE, TRAIN, AND EVALUATE LSTM
		# *********************************************************
		print 'Creating, training and evaluating LSTM...'
		numOfOutcomes = len(CARDIAC_EVENTS)
		(sensitivity, specificity) = runModel(trainingX, trainingY, testingX, testingY, verboseFile)
		sensitivities[timeBeforeIndex][timeWindowIndex] = sensitivity
		specificities[timeBeforeIndex][timeWindowIndex] = specificity

		print 'Completed! \n'

# *********************************************************
# PUT SENSITIVITY AND SPECIFICITY
# *********************************************************

# Print sensitivity
overviewFile.write('Each column represents a different time window and each row represents a different time before beginning of cardiac event.  The first row and column contain the values of these variables.\n\n')

np.set_printoptions(precision=3)

# Print timeWindows.
overviewFile.write('***********************\nTime Windows\n**********************\n\n')
overviewFile.write(str(timeWindows))
overviewFile.write('\n\n')

# Print timeBefores.
overviewFile.write('*************************\nTime Before Beginning of Cardiac Event\n************************\n\n')
overviewFile.write(str(timeBefores))
overviewFile.write('\n\n')

# Print specificity.
overviewFile.write('*************************\nSensitivity\n************************\n\n')
overviewFile.write(str(specificities))
overviewFile.write('\n\n')

# Print sensitivity.
overviewFile.write('*************************\nSpecificity\n************************\n\n')
overviewFile.write(str(sensitivities))
overviewFile.write('\n\n')

# *********************************************************
# CLOSE THE TWO FILES
# *********************************************************
overviewFile.close()
verboseFile.close()

# *********************************************************
# SAVE SENSITIVITY AND SPECIFICITY TO FILE
# *********************************************************
sensitivitiesFileName = '../results/sensitivities.pickle'
with open(sensitivitiesFileName, 'w') as f:
	pickle.dump([sensitivities], f)

specificitiesFileName = '../results/specificities.pickle'
with open(specificitiesFileName, 'w') as f:
	pickle.dump([specificities], f)
