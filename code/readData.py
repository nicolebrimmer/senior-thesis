'''
	This file contains the methods required to read the ECG data and annotations contained within
	the .atr, .dat, and .hea files and store it within a list of objects of the class [DatabaseData].
    
        Each object of the class [DatabaseData] represents a single database of ECG signals and contains
        a list of objects of the class [PatientData].
    
        Each object of the class [PatientData] represents a single patient within a single database of 
        ECG signals and contains a list of 
        
        Each object of the class [Beat] represents a single heart beat of a single patient within a single
        database of ECG signals and contains a list of ECG signals in the form of an n x (s + 1) 
        array of numbers, where n is the number of ECG signals in the beat and s is the number of leads 
        used to measure the ECG signal.
        The first column in the array of numbers contains the time stamps of the various ECG measurements.

	Note: These methods are not gauranteed (and are in fact very unlikely) to work when you have any 
    vim sessions open in any of the databases.

'''

import os
import ntpath
import matplotlib.pyplot as plt
import numpy as np
import scipy


from beat import Beat
from ecgReading import ECGReading

# CONSTANTS
DATABASE_DIR = "../../ecg-data2/"
DATA_EXTENSION = "-dat"
ANNOTATION_EXTENSION = "-ann"

# A dictionary containing descriptions of the abbrevations of many cardiac events.
TYPES_OF_ALL_EVENTS_DICT = {'(AB': 'Atrial bigeminy',
                            '(AFIB': 'Atrial fibrillation',
                            '(AFL': 'Atrial flutter',
                            '(B':	'Ventricular bigeminy',
                            '(BII': '2 degree heart block',
                            '(IVR': 'Idioventricular rhythm',
                            '(N':	'Normal sinus rhythm',
                            '(NOD': 'Nodal (A-V junctional) rhythm',
                            '(P': 'Paced rhythm',
                            '(PREX': 'Pre-excitation (WPW)',
                            '(SBR': 'Sinus bradycardia',
                            '(SVTA': 'Supraventricular tachyarrhythmia',
                            '(T':	'Ventricular trigeminy',
                            '(VFL': 'Ventricular flutter',
                            '(VT': 'Ventricular tachycardia'}

# A dictionary containing descriptions of the abbreviations of the cardiac events
# whose occurrence the LSTM will attempt to predict. 
TYPES_OF_EVENTS_DICT = {'(AB': 'Atrial bigeminy',
                        '(AFIB': 'Atrial fibrillation',
                        '(B':   'Ventricular bigeminy',
                        '(N':   'Normal sinus rhythm',
                        '(SBR': 'Sinus bradycardia',
                        '(SVTA': 'Supraventricular tachyarrhythmia',
                        '(T':   'Ventricular trigeminy',
                        '(VT': 'Ventricular tachycardia'}

CARDIAC_EVENTS = TYPES_OF_EVENTS_DICT.keys()

def getDatabases():
	'''
	Returns a vector containing the full (relative) paths of the roots of all of the directories in [DATABASE_DIR].  Each
    directory in [DATABASE_DIR] is assumed to correspond to a database of ECG signals that has been downloaded manually.
    
    Relative paths have been chosen over absolute paths since this program will be run on both Nikki's personal laptop 
    and on safar.
    
	'''

	return [os.path.join(DATABASE_DIR, entry) for entry in os.listdir(DATABASE_DIR) if os.path.isdir(os.path.join(DATABASE_DIR, entry))]
	 
def getPatientNames(databaseName):
	'''
	Returns a vector containing the "names" of all patients (e.g. "100") whose ECG records have been downloaded into
	the database whose full relative path name is [databaseName].

	Note that if "100" is in the vector returned by this method, all of the following files must be in the directory 
    [databaseName] - 100.cat, 100.dat, 100.hea

	'''
    
	fullFileNames = [os.path.join(databaseName, entry) for entry in os.listdir(databaseName) if os.path.isfile(os.path.join(databaseName, entry))]

	patientNames = []
	patientNamesDict = {}
	for fullFileName in fullFileNames:
		# Extract out the file name from the entire path name.
		head, tail = ntpath.split(fullFileName)
    		fileName = tail or ntpath.basename(head)
		
		# Split into the name and the extension.
		patientName, extension = fileName.split(".")

		if (patientName in patientNamesDict):
			patientNamesDict[patientName].append(extension)

			# Check if all of the desired extensions are associated with the current
			# file name being considered.
			currentExtensions = patientNamesDict[patientName]
			if ("atr" in currentExtensions and "dat" in currentExtensions and "hea" in currentExtensions and len(currentExtensions) == 3):
				patientNames.append(patientName)
		else:
			patientNamesDict[patientName] = [extension]

	patientNames.sort()
	return patientNames

def createTextFiles():
	'''
	Loops through all of the patients whose ECG readings have been downloaded (manually) into a database directory within
    the directory [DATABASE_DIR] and for each such patient, runs the rdsamp and rdann WFDB commands to produce a text file
    that contains the data and annotations associated with the patient.  
    
    Two text files are produced:
        (1) [patientName]-[DATA_EXTENSION].txt
            This text file contains the ECG signals (i.e. data) associated with the patient named 
            [patientName] (e.g. [patientName] = "100").
            
            An example of the first three lines of such a produced text file is shown below.
            Elapsed time    MLII      V1
            (seconds)       (mV)      (mV)
            0.000           0.350     0.105
            
            Note that the first two lines do not contain any data (but increases readability of the file).  Each text 
            file will contain (d + 1) columns where d is the number of leads used to collect data from the specified 
            patient.  The value of d can vary from patient to patient.
            
        (2) [patientName]-[ANN_EXTENSION].txt
            This text file contains the annotations associated with the patient named
            [patientName] (e.g. [patientName] = "100").
            
            An example of the first three lines of such a produced text file is shown below.
            Time       Sample #  Type  Sub Chan  Num      Aux
            0:00.186       67     +    0    0    0        (B
            0:00.625      225     V    1    0    0

            Note that the first line does not contain any data (but increases readability of the file).  An explanation of 
            the meaning of each of these columns can be found online at the following website:
            https://www.physionet.org/physiobank/annotations.shtml
    
    These two text files are saved to the same directory as the source files - [patientName].cat, [patientName].dea, [patientName].hea -
    and are saved to the directory [databaseName] within [DATABASE_DIR].
    
	'''
	
	databaseNames = getDatabases()
	for databaseName in databaseNames:
		patientNames = getPatientNames(databaseName)
		
		for patientName in patientNames:
			# Change directories into the database.
        		cdBashCommand = "cd \"" + databaseName + "\""

        		# Run the bash command to produce a text file containing the ECG signal.
        		rdSampBashCommand = "rdsamp -r \"" + patientName + "\" -p -v >\"" + patientName + DATA_EXTENSION + ".txt\""
			print (cdBashCommand + "; " + rdSampBashCommand)
			os.system(cdBashCommand + "; " +  rdSampBashCommand)

			# Run the bash command to produce a text file containing the annotations for the ECG signal.
			rdAnnBashCommand = "rdann -r \"" + patientName + "\" -a atr -v >\"" + patientName + ANNOTATION_EXTENSION + ".txt\""
			print (cdBashCommand + "; " + rdAnnBashCommand)
			os.system(cdBashCommand + "; " + rdAnnBashCommand)

def getBeatsFromAnn(databaseName, patientName):
	'''
	Reads the annotation text file associated with the ECG signal for patient [patientName] in database [databaseName]
	and produces (and returns) a list of tuples of the form ([beginSampleIndex], [endSampleIndex], [typeOfBeat], [auxillary]).  Each such
    tuple represents an ECG beat.

	This list of tuples divides the ECG signal associated with the specified patient into beats.  Each tuple in the list
	is associated with a beat in the ECG signal.  The (beginSampleIndex + 1)-th sample in the patient's ECG signal is the first
	sample in the beat and the (endSampleIndex + 1)-th sample in the patient's ECG signal is the last sample in the beat.  
    The type of beat is specified by [typeOfBeat].  The type of rhythm the beat is a part of specified by [auxillary].
    
    The strings [typeOfBeat] and [auxillary] are annotations whose meanings are explained online at the following website:
    https://www.physionet.org/physiobank/annotations.shtml

	'''

	# Construct the full file name (path and all) of the text file that contains the annotations for [patientName]
	# in [databaseName].
	fullFileName = os.path.join(databaseName, patientName) + ANNOTATION_EXTENSION + ".txt"

	f = open(fullFileName, 'r')

	listOfBeats = []

	# Loop through the lines in the text file.  The first line in the file is a header and should be ignored.
	lineIndex = 0
	lastSampleIndex = 0
	lastAux = ""
	for line in f:
		# If this line is not the first line in the file, then this line contains data.
		if (lineIndex != 0):
			dataArr = line.split()
			
			currSampleIndex = int(dataArr[1])
			beatType = dataArr[2]

			# Subtract 1 from the indices because we would like to work with zero-indexing
			# but the indices in the text file appear to be one-indexing.
                        beatTuple = (lastSampleIndex - 1, currSampleIndex - 1, beatType, lastAux)
                        listOfBeats.append(beatTuple)

			# If this line contains an element in the "aux" column, update last aux
			if (len(dataArr) == 7):
				lastAux = dataArr[6]

			lastSampleIndex =  currSampleIndex + 1
		
		lineIndex = lineIndex + 1

	f.close()

	# Remove the first and last tuple because they will correspond to incomplete beats.
	listOfBeats.pop(0)
	listOfBeats.pop()

	return listOfBeats


def getECGSignalFromDat(databaseName, patientName):
    
	''' 
	Reads the data text file associated with the ECG signal for patient [patientName] in database [databaseName]
	and produces (and returns) a [numOfSamples] x (1 + [numOfDataSources]) two-dimensional array, where [numOfSamples] 
    is the number of samples in the ECG signal and [numOfDataSources] is the number of data sources.  For instance, if 
    the ECG signal for a particular patient in a particular database was collected from 3 leads, then [numOfDataSources] = 3.

	'''
	
	# Construct the full file name (path and all) of the text file that contains the annotations for [patientName]
	# in [databaseName].
	fullFileName = os.path.join(databaseName, patientName) + DATA_EXTENSION + ".txt"

	f = open(fullFileName, 'r')
	
	ecgData = []

	# Loop through the lines in the text file.  The first two lines in the file are a header and should be ignored.
	lineIndex = 0
	for line in f:
		# If this line is not the first two lines in the file, then this line contains contains data.
		if (lineIndex != 0 and lineIndex != 1):
			dataArr = line.split()

			# Convert the ecg signal from a string into integers.
			dataArr = [float(dataArrElement) for dataArrElement in dataArr]
			ecgData.append(dataArr)
	
		lineIndex = lineIndex + 1
    
	f.close()

	return ecgData

def getLeadNames(databaseName, patientName):
	'''
    
	Returns a vector containing the names of all of leads that have been used to collect ECG signals from the patient
	[patientName] in the database [databaseName] in the order in which they are recorded in the data text file associated 
	with the specified patient.
    
	'''

	# Construct the full file name (path and all) of the text file that contains the annotations for [patientName]
	# in [databaseName].
	fullFileName = os.path.join(databaseName, patientName) + DATA_EXTENSION + ".txt"
    
	f = open(fullFileName, 'r')

	# The information is included in only the first line of the file.
	firstLine = f.readline()
	f.close()
	leadNames = firstLine.split()

	# Remove the first two elements of the array, corresponding to the strings heading the "Elapsed Time" column
	# of the ECG data textfile.
	leadNames.pop(0)
	leadNames.pop(0)

	return leadNames

def getBeatFromDat(listOfBeats, ecgData, beatNum, leadNum):
	'''
	Returns an object of the [Beat] class that contains the data associated with the (beatNum + 1)-th beat and
	(leadNum + 1)-th lead of the ECG signal associated with the patient whose list of beats is specified by the list of
	tuples [listOfBeats] (see the documentation for the above method getBeatsFromAnn for a full description of [listOfBeats])
	and whose ECG signal is specified by the array [ecgData] (see the documentation for the above method getECGSignalFromDat for
	a full description of [ecgData].
    
	'''
    
	(beginSampleIndex, endSampleIndex, typeOfBeat, auxillary) = listOfBeats[beatNum]
    
	timeStamps = []
	ecgReadings = []
    
	for index in range(beginSampleIndex, endSampleIndex + 1):
		sample = ecgData[index]
        
        	timeStamps.append(sample[0])
        	ecgReadings.append(sample[leadNum + 1])

    	return Beat(timeStamps, ecgReadings, typeOfBeat, auxillary)

def getData(amountOfTimeBeforeBeg, timeWindow, doCreateTextFiles):
	'''
	Determines and returns a complete list of [Beats] objects, each [Beats] object representing a
	portion of an ECG signal that has been downloaded from MIMIC II into one of the sub-directories in 
	the directory ../../ecg-data2/ (each sub-directory in the directory ../../ecg-data2/ represents a
	database of ECG signals collected from ICU patients) and that begins [amountOfTimeBeforeBeg]
	seconds (or a little bit more than [amountOfTimeBeforeBeg] seconds) before an abnormal cardiac event
	and that is [timeWindow] seconds (or a little bit less than [timeWindow] seconds) in duration.

	Creates the text file representations of the ECG data and annotations if and only if [doCreateTextFiles]
	= True.  Otherwise, the text file representations are not created and it is assumed that they have
	already been created.
	'''
	if (doCreateTextFiles):
		createTextFiles()

	# Contains a list of [Beats] objects.
	listOfBeatsObjs = []

	databaseNames = [getDatabases()[0]]
	for databaseName in databaseNames:
		print '**************************************'
		print 'Working on database ' + str(databaseName)
		print '**************************************'
		patientNames = getPatientNames(databaseName)
	
		'''
		if (databaseName == getDatabases()[0]):
			proportion = 25
		else:
			proportion = 36
		'''
		for patientName in patientNames:
			print 'Working on patient ' + str(patientName)
			listOfBeats = getBeatsFromAnn(databaseName, patientName)
			ecgData = getECGSignalFromDat(databaseName, patientName)
			leadNames = getLeadNames(databaseName, patientName)

			for leadNum in range(len(leadNames)):
				leadName = leadNames[leadNum]
				beats = []
				for beatNum in range(len(listOfBeats)):
					beat = getBeatFromDat(listOfBeats, ecgData, beatNum, leadNum)
					#beat.resample(proportion)
					beats.append(beat)
				
				ecgReading = ECGReading(databaseName, patientName, leadName, beats)
				beatsObjs = ecgReading.createBeatsObjs(amountOfTimeBeforeBeg, timeWindow)

				for beatsObj in beatsObjs:
					if (beatsObj is not None):
						listOfBeatsObjs.append(beatsObj)				
	auxNum = {}
	for cardiacEvent in CARDIAC_EVENTS:
		auxNum[cardiacEvent] = 0	

	for beatsObj in listOfBeatsObjs:
		auxNum[beatsObj.getCardiacEvent()] = auxNum[beatsObj.getCardiacEvent()] + 1

	for cardiacEvent in auxNum:
		print ('The number associated with ' + str(cardiacEvent) + ' is ' + str(auxNum[cardiacEvent]))

	return listOfBeatsObjs
