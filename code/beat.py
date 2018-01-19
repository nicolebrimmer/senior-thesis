'''
    This file contains the definition of the class 'Beat', each object of which is
    associated with a single beat and contains the data and annotations associated
    with said beat.
    
    
'''

import matplotlib.pyplot as plt
import numpy as np

class Beat(object):

    def __init__(self, timeStamps, ecgReadings, typeOfBeat, auxillary):
        '''
            Creates an object of class [Beat]
            
        '''
        
        # Fields containing information about the actual ECG data associated with the
        # beat (i.e. the data).
        self.timeStamps = timeStamps
        self.ecgReadings = ecgReadings
        
        # Fields containing information about the annotations associated with the beat.
        self.typeOfBeat = str(typeOfBeat)
        self.auxillary = str(auxillary)
    
    def getLastTimeStamp(self):
        '''
            Returns the time stamp of the last sample in this beat.
        '''
        
        return self.timeStamps[len(self.timeStamps) - 1]
    
    def getFirstTimeStamp(self):
        '''
            Returns the time stamp of the first sample in this beat.
        '''
    
        return self.timeStamps[0]
    
    def getAux(self):
        '''
            Returns the auxillary field of this beat, i.e. the short string abbreviation for 
            the type of cardiac rhythm this beat is a part of.
        '''
        return self.auxillary
    
    def getECGReadings(self):
	'''
	    Returns an array of the ecg readings.
	'''
	return self.ecgReadings

    def resample(self, proportion):
	self.ecgReadings = self.ecgReadings[::proportion]
	self.timeStamps = self.timeStamps[::proportion]

    def plotBeat(self, plotNameExtension):
        '''
            Saves a plot of this beat (i.e. a plot of the time stamps along the x-axis
            and the ECG readings along the y-axis) as the file, 'plotOfBeat[plotNameExtension].png' in the directory
            '../results'
            
        '''
	plt.figure()    
        plt.plot(self.timeStamps, self.ecgReadings)
        plt.savefig("../results/" + str(plotNameExtension) + "plotOfBeat.png")
    
    def isPartOfAux(self, aux):
        ''' 
            Returns true if and only if the current Beat object represents a beat that is 
            a part of the rhythm described by the string abbreviation [aux] (e.g. '(AB').
            Note that the string [aux] must be a key in the dictionary [TYPES_OF_EVENTS_DICT] 
            defined in readData.py.
            
        '''
    
        return self.auxillary == aux

    def getNumpyArr(self):
        '''
            Returns a numpy array representation of the current Beat object.

            The returned numpy array arr has 2 rows, the first row containing time stamps 
            and the second row containing ECG signal readings.  Note that arr[2, n] is the
            ECG signal reading taken at time arr[1, n]. 
        '''

        numOfRows = 2
	numOfCols = len(self.timeStamps)
        arr = np.ones((numOfRows, numOfCols))

	for col in range(numOfCols):
            arr[0, col] = self.timeStamps[col]
            arr[1, col] = self.ecgReadings[col]

	return arr
            	

    def __str__(self):
        # Heading
        str1 = ' ****** BEAT OBJECT ********* \n \n'
        
        # Annotations
        str1 = str1 + 'Type of Beat: ' + self.typeOfBeat + '\n'
        str1 = str1 + 'Auxillary: ' + self.auxillary + '\n \n'
        
        # ECG Readings
        str1 = str1 + 'ECG Readings: \n\n'
        
        for index in range(len(self.timeStamps)):
            str1 = str1 + 'Time Stamp: ' + str(self.timeStamps[index]) + ' ECG Reading: ' + str(self.ecgReadings[index]) + '\n\n'
        
        # Temporarily testing the getLastTimeStamp and getFirstTimeStamp.
        str1 = str1 + 'First Time Stamp: ' + str(self.getFirstTimeStamp()) + '\n\n'
        str1 = str1 + 'Last Time Stamp: ' + str(self.getLastTimeStamp()) + '\n\n'
	 
        return str1




