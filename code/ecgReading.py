'''
    This file contains the definition of the class 'ECGReading', each object of which is
    associated with a single lead and contains all of the data and annotations associated with 
    the ECG data from one patient in one database collected from one lead.

'''

from beat import Beat
from beats import Beats
import readData

class ECGReading:

    def __init__(self, databaseName, patientName, leadName, beats):
        ''' 
            Creates an object of class [ECGReading]
            
            [beats] is a list of objects of the class [Beat].  Each element in this list represents
            a single ECG beat that was collected from one patient (whose name is [patietName]) and one lead
            (whose name is [leadName]) and that is stored in one database (whose name is [databaseName]).  
            The order of the elements in the list [beat] is the order with which the beats were collected.
            
        '''

        # Fields containing information about the means of collection
        self.databaseName = str(databaseName)
        self.patientName = str(patientName)
        self.leadName = str(leadName)
        
        # Fields containing information about the actual ECG readings (and the actual ECG beats)
        self.beats = beats
    
    def getIndexOfLastBeatEndingBefore(self, timeStamp):
        '''
            Loops through [beats], the list of [Beat] objects associated with this [ECGReading] object,
            and returns the index of the last [Beat] object in [beats] that ends before the time stamp
            [timeStamp], which is measured in seconds that have elasped since the beginning of the reading.
            
            If there is no such [Beat] object (i.e. there is no [Beat] object that ends before the time stamp
            [timeStamp] in this [ECGReading] object), then -1 (an invalid index) is returned.
            
        '''
        lastIndex = -1
        lastEndTimeStamp = 0
    
        # Loop through all of the beats in the ECGReading object.
        for index in range(len(self.beats)):
            beat = self.beats[index]
            
            endTimeStamp = beat.getLastTimeStamp()

            # If the current beat ends after the specified time stamp, then break out of the loop.
            # You have gone slightly too far.
            if (endTimeStamp > timeStamp):
                return lastIndex
            
            # Otherwise, you need to update things for the next iteration of the for loop.
            else:
                lastIndex = index
                lastEndTimeStamp = endTimeStamp
    
        return -1
                
    
    def getIndexOfFirstBeatBegAfter(self, timeStamp):
        '''
            Loops through [beats], the list of [Beat] objects associated with this [ECGReading] object,
            and returns the index of the first [Beat] object in [beats] that begins after the time stamp
            [timeStamp], which is measured in seconds that have elasped since the beginning of the reading.
            
            If there is no such [Beat] object (i.e. there is no [Beat] object that begins after the time stamp
            [timeStamp] in this [ECGReading] object, then -1 (an invalid index) is returned.
            
            If the first [Beat] object in this [ECGReading] object begins before the specified time stamp [timeStamp],
            then -1 (an invalid index) is returned.
                                               
        '''
        
        # If the time stamp is even before the first beat, then return -1.
        if (timeStamp < self.beats[0].getFirstTimeStamp()):
            return -1
        
        # Loop through all of the beats in the ECGReading object.
        for index in range(len(self.beats)):
            beat = self.beats[index]
            
            begTimeStamp = beat.getFirstTimeStamp()
            
            # If the current beat begins after the specified time stamp, then it is the first to do so.
            if (begTimeStamp >= timeStamp):
                return index
        
        return -1
    
    def getIndicesOfBegOfAux(self):
        ''' 
            Loops through [beats], the list of [Beat] objects associated with this [ECGReading] object, and returns an array of tuples
            containing the indicies of the first [Beat] object in each abnormal cardiac rhythm and the abbreviated string
            descriptions of abnormal cardiac rhythm.  This string abbreviation must be a key in the dictionary [TYPES_OF_EVENTS_DICT]
            defined in readData.py.
            
            If arr is the returned 2D array, then ...
                * Each row of arr[n] represents an abnormal cardiac rhythm.
                * The first element in the tuple in the (n + 1)-th row in arr is the value of [begIndex], where
                  [begIndex] is the index of the first [Beat] object in this particular abnormal cardiac rhythm.
                * The second element in the tuple in the (n + 1)-th row in arr is the value of [aux], where [aux] is
                  the string abbreviation for the abnormal cardiac rhythm.
            
        '''
    
        lastAux = ""
        arr = []
    
        for index in range(len(self.beats)):
            beat = self.beats[index]
            aux = beat.getAux()
            
            # If this is the first beat in the new cardiac rhythm,...
            if (lastAux != aux):

                # If this beat is part of a cardiac rhythm of interest,...
                if (aux in readData.TYPES_OF_EVENTS_DICT):
                    arr.append((index, aux))

                lastAux = aux
        
        return arr

    def createBeatsObj(self, begAuxIndex, aux, amountOfTimeBeforeBeg, timeWindow):
        '''
                Returns a [Beats] object, that is associated with a list of contiguous [Beat] objects that starts with the 
                first [Beat] object that begins less than ([amountOfTimeBeforeBeg] + [timeWindow]) seconds before the
                ([begAuxIndex] + 1)-th [Beat] object in this [ECGReading] object and that ends with the last [Beat] object
                that ends less than [amountOfTimeBeforeBeg] seconds before the ([begAuxIndex] + 1)-th [Beat] object in this [ECGReading] object.
                
                Note that the (begAuxIndex + 1)-th [Beat] object in this [ECGReading] object is the first beat in an abnormal
                cardiac rhythm.  [aux] is an abbreviated string description of the abnormal cardiac rhythm.  This string abbrevation
                must be a key in the dictionary [TYPES_OF_EVENTS_DICT] defined in readData.py.
        '''

        auxTimeStamp = self.beats[begAuxIndex].getFirstTimeStamp()
 
        begTimeStamp = auxTimeStamp - (amountOfTimeBeforeBeg + timeWindow)
        endTimeStamp = auxTimeStamp - (amountOfTimeBeforeBeg)
 
        begIndex = self.getIndexOfFirstBeatBegAfter(begTimeStamp)
        endIndex = self.getIndexOfLastBeatEndingBefore(endTimeStamp)
    
        if (begIndex == -1 or endIndex == -1):
            return None

        else:
            listOfBeatObjs = []
            
            for index in range(begIndex, endIndex + 1):
                listOfBeatObjs.append(self.beats[index])
		
            if (len(listOfBeatObjs) == 0):
                return None
            else:
                return Beats(self.databaseName, self.patientName, self.leadName, amountOfTimeBeforeBeg, timeWindow, aux, auxTimeStamp, listOfBeatObjs)

    def createBeatsObjs(self, amountOfTimeBeforeBeg, timeWindow):
        '''
            Returns a list of [Beats] objects.  For every abnormal cardiac rhythm beginning at the ([begAuxIndex] + 1)-th [Beat] object
            in this [ECGReading] object, if possible, there is an element in this list, a [Beats] object, that is associated with a list of
            contiguous [Beat] objects that starts with the first [Beat] object that begins less than ([amountOfTimeBeforeBeg] + 
            [timeWindow]) seconds before the (begAuxIndex + 1)-th [Beat] object in this [ECGReading] object and that ends with the last [Beat] object
            that ends less than [amountOfTimeBeforeBeg] seconds before the (begAuxIndex + 1)-th [Beat] object in this [ECGReading] object.
            
        '''
        
        listOfBeatsObjs = []
        for (begIndex, aux) in self.getIndicesOfBegOfAux():
            beatsObj = self.createBeatsObj(begIndex, aux, amountOfTimeBeforeBeg, timeWindow)

            if (beatsObj is not None):
                listOfBeatsObjs.append(beatsObj)

        return listOfBeatsObjs

    def __str__(self):
        # Heading
        str1 = ' ****** ECG READING OBJECT ********* \n \n'

        # Information about means of collection
        str1 = str1 + 'Database Name: ' + self.databaseName + '\n'
        str1 = str1 + 'Patient Name: ' + self.patientName + '\n'
        str1 = str1 + 'Lead Name: ' + self.leadName + '\n \n'

	'''
        # Information about the beats themselves
        for beat in self.beats:
            str1 = str1 + str(beat)

        str1 = str1 + '\n\n'
	'''
        return str1
