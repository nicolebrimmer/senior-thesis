'''
    This file contains the definition of the class 'Beats', each object of which is associated with 
    a list of objects of the class [Beat], which together spans a time period of at most [timeWindow] seconds.  
    
    Three important notes about this list of [Beat] objects:
        (1) This list of [Beat] objects in an object on this class is in the order of their occurrence in the ECG
            recording of patient [patientName] from lead [leadName] that is stored in the database [databaseName].
        
        (2) The first beat in this list is the first beat in the corresponding ECG reading that begins less than
            ([timeBefore] + [timeWindow]) seconds before the beginning of the event [cardiacEvent] in the corresponding
            ECG reading.
    
        (3) The last beat in this list is the last beat in the corresponding ECG reading that ends more than 
            ([timeBefore]) seconds before the beginnning of the event [cardiacEvent] in the correspodnign ECG reading.
            
    [cardiacEvent] is the string abbreviation of a cardiac event, e.g. '(AB').  Note that the string
    [cardiacEvent] must be a key in the dictionary [TYPES_OF_EVENTS_DICT] defined in readData.py.
    
    [cardiacEvent] begins as soon as [cardiacEventBegTimeStamp] seconds have elapsed in the specified patient's ECG
    reading.
'''

from beat import Beat
import numpy as np

class Beats:

    def __init__(self, databaseName, patientName, leadName, timeBefore, timeWindow, cardiacEvent, cardiacEventBegTimeStamp, beats):
        
        # Fields containing information about the patient and the source of this data.
        self.databaseName = databaseName
        self.patientName = patientName
        self.leadName = leadName

        # Fields containing information about the relation between the list of [Beat] objects associated with this object
        # and the cardiac event in the corresponding ECG reading.
        self.timeBefore = timeBefore
        self.timeWindow = timeWindow
        self.cardiacEvent = cardiacEvent
	self.cardiacEventBegTimeStamp = cardiacEventBegTimeStamp

        # Fields containing the list of [Beat] objects.
        self.beats = beats


    def getCardiacEvent(self):
        '''
            Returns the string abbreviation of the cardiac event that this [Beats] object precedes.  Note that the
            returned string must be a key in the dictionary [TYPES_OF_EVENTS_DICT] defined in readData.py.
        '''

        return self.cardiacEvent

    def getNumOfBeats(self):
	'''
	    Returns the number of [Beat] objects associated with the current [Beats] object.
	'''
	return len(self.beats) 

    def getMaxLengthOfBeat(self):
	'''
	    Returns the maximum number of ECG readings associated with any single [Beat] object
	    in the current [Beats] object.
	'''
	maxLengthOfBeat = 0
	for beat in self.beats:
		lengthOfBeat = len(beat.getECGReadings())
		maxLengthOfBeat = max(maxLengthOfBeat, lengthOfBeat)

	return maxLengthOfBeat

    def getBeats(self):
	'''
            Returns the list of [Beat] objects associated with the current [Beats] object.
	'''
	return self.beats
	
    def getNumpyArr(self):
        '''
             Returns the numpy array representation of the current [Beats] object.
   
             The returned numpy array has 1 row and this row contains the numpy array 
             representations of each of the [Beat] objects contained in the current [Beats]
             object in the order in which the [Beat] objects occurred.

	     DOES NOT WORK SINCE NUMPY CANNOT BE RAGGED
        '''
       
        numOfRows = 1
        numOfCols = len(self.beats)
        arr = np.ones((numOfRows, numOfCols))

        for col in range(numOfCols):
            arr[0, col] = self.beats[col].getNumpyArr()

	return arr


    def getArr(self):
        '''
             Returns the array representation of the current [Beats] object.
   
             The returned array has 1 row and this row contains all of the ecg readings.

	     DOES NOT WORK SINCE ARR CANNOT BE RAGGED
        '''

	arr = []
        for beat in self.beats:
            arr.extend(beat.getECGReadings())
	
	return arr


    def __str__(self):

        # Heading
        str1 = ' ****** BEATS OBJECT ********* \n \n'
        
        # Information about means of collection
        str1 = str1 + 'Database Name: ' + self.databaseName + '\n'
        str1 = str1 + 'Patient Name: ' + self.patientName + '\n'
        str1 = str1 + 'Lead Name: ' + self.leadName + '\n \n'
        
        # Information about the relation between the list of [Beat] objects associated with this object
        # and the cardiac event in the corresponding ECG reading.
        str1 = str1 + 'Time Before Cardiac Event: ' + str(self.timeBefore) + ' seconds \n'
        str1 = str1 + 'Length of Window of Time: ' + str(self.timeWindow) + ' seconds \n'
        str1 = str1 + 'Cardiac Event: ' + str(self.cardiacEvent) + '\n'
	str1 = str1 + 'Cardiac Event Beginning Time Stamp: ' + str(self.cardiacEventBegTimeStamp) + ' seconds \n\n'

	print str1
	print 'The length of the beats: ' + str(len(self.beats)) + '\n\n'

	# Information about the beginning and end of the list of [Beat] objects associated with this object.
	begTimeStamp = self.beats[0].getFirstTimeStamp()
	endTimeStamp = self.beats[len(self.beats) - 1].getLastTimeStamp()
	str1 = str1 + 'Beginning Time Stamp: ' + str(begTimeStamp) + ' seconds \n'
	str1 = str1 + 'Ending Time Stamp: ' + str(endTimeStamp) + ' seconds \n\n'
	        
        # Information about the beats themselves
	'''
        for beat in self.beats:
            str1 = str1 + str(beat)
        
        str1 = str1 + '\n\n'
        '''
        return str1

