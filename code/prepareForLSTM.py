'''
    This file includes all of the methods required to prepare [listOfBeats], a vector of [Beats] objects
    for training and evaluating the LSTM model that will used to predict VT episodes.
    
'''

import random
import numpy as np

import readData

np.random.seed(1337)  # for reproducibility

def divideIntoTrainingAndTesting(listOfBeatsObjs, trainingFract):
    '''
        Divides [listOfBeatsObjs], a vector of [Beats] objects, into [trainingObjs], a vector of [Beats] objects
        that will be used to train the LSTM, and [testingObjs], a vector of [Beats] objects that will
        be used to test the LSTM.
        
        Returns a vector of the form ([trainingObjs], [testingObjs])
        
        [trainingFract] fraction of the [Beats] objects in [listOfBeatsObjs] will be in [trainingObjs] and the rest of
        the [Beats] objects will be in [testingObjs].
    '''

    # Create a dictionary that keeps track of the number of [Beats] objects
    # associated with each cardiac event and the indices of these [Beats] objects.
    numOfEachAux = {}
    for aux in readData.TYPES_OF_EVENTS_DICT:
        numOfEachAux[aux] = [0, []]

    # Calculate the values of the entries of the dictionary that keeps track of the number
    # of [Beats] objects associated with each cardiac event and the indices of these [Beats] objects.
    for index in range(len(listOfBeatsObjs)):
        aux = listOfBeatsObjs[index].getCardiacEvent()
        numOfEachAux[aux][0] = numOfEachAux[aux][0] + 1
        numOfEachAux[aux][1].append(index)

    trainingIndices = []

    # Determine the number of [Beats] objects associated with each cardiac event and use that
    # to determine the indices of the [Beats] objects associated with each cardiac event that will
    # used to train the LSTM.
    for aux in numOfEachAux:
        listOfIndices = numOfEachAux[aux][1]
            
        numOfTrainingBeats = int(round(trainingFract * len(listOfIndices)))
        trainingBeatsIndices = random.sample(listOfIndices, numOfTrainingBeats)
            
        trainingIndices.extend(trainingBeatsIndices)


    trainingObjs = []
    testingObjs = []

    for index in range(0, len(listOfBeatsObjs)):
        beatsObj = listOfBeatsObjs[index]
        if (index in trainingIndices):
            trainingObjs.append(beatsObj)
        else:
            testingObjs.append(beatsObj)

    np.random.shuffle(trainingObjs)
    np.random.shuffle(testingObjs)

    return (trainingObjs, testingObjs)


def convertIntoNumpyArrays(listOfBeatsObjs, trainingObjs, testingObjs):
    '''
       Convert [trainingObjs], a vector of [Beats] objects that will be used to train the LSTM, and 
       [testingObjs], a vector of [Beats] objects that will used be used to test the LSTM into Numpy Arrays.
       
       Returns a tuple of the form ([trainingX], [trainingY], [testingX], [testingY])
    '''
    # Determine the maximum number of beats in a sequence.
    maxNumOfBeats = 0
    for beatsObj in listOfBeatsObjs:
        maxNumOfBeats = max(maxNumOfBeats, beatsObj.getNumOfBeats())

    # Determine the maximum number of ecg readings in a beat.
    maxLengthOfBeat = 0
    for beatsObj in listOfBeatsObjs:
        maxLengthOfBeat = max(maxLengthOfBeat, beatsObj.getMaxLengthOfBeat())


    numOfTraining = len(trainingObjs)
    numOfTesting = len(testingObjs)
    numOfOutcomes = len(readData.CARDIAC_EVENTS)

    # Initialize the arrays.
    trainingX = np.zeros((numOfTraining, maxNumOfBeats, maxLengthOfBeat), dtype=np.float64)
    trainingY = np.zeros((numOfTraining, numOfOutcomes), dtype=np.float64)

    testingX = np.zeros((numOfTesting, maxNumOfBeats, maxLengthOfBeat), dtype=np.float64)
    testingY = np.zeros((numOfTesting, numOfOutcomes), dtype=np.float64)

    # Create training numpy arrays.
    for sequenceIndex in range(numOfTraining):
        sequenceOfBeats = trainingObjs[sequenceIndex].getBeats()
	diff = maxNumOfBeats - len(sequenceOfBeats)            

        for beatIndex in range(len(sequenceOfBeats)):
        	ecgReadings = sequenceOfBeats[beatIndex].getECGReadings()
		ecgReadings = np.ndarray.tolist(np.pad(ecgReadings, (maxLengthOfBeat - len(ecgReadings), 0), 'constant', constant_values=(0, 0)))
                    
                for ecgReadingIndex in range(len(ecgReadings)):
                    ecgReading = ecgReadings[ecgReadingIndex]
                    trainingX[sequenceIndex, beatIndex, ecgReadingIndex] = ecgReading

        cardiacEventIndex = readData.CARDIAC_EVENTS.index(trainingObjs[sequenceIndex].getCardiacEvent())
        trainingY[sequenceIndex, cardiacEventIndex] = 1

    # Create testing numpy arrays.
    for sequenceIndex in range(numOfTesting):
        sequenceOfBeats = testingObjs[sequenceIndex].getBeats()
	diff = maxNumOfBeats - len(sequenceOfBeats)
            
        for beatIndex in range(len(sequenceOfBeats)):
                ecgReadings = sequenceOfBeats[beatIndex].getECGReadings()
		ecgReadings = np.ndarray.tolist(np.pad(ecgReadings, (maxLengthOfBeat - len(ecgReadings), 0), 'constant', constant_values=(0, 0)))
                    
                for ecgReadingIndex in range(len(ecgReadings)):
                        ecgReading = ecgReadings[ecgReadingIndex]
                        testingX[sequenceIndex, beatIndex, ecgReadingIndex] = ecgReading

        cardiacEventIndex = readData.CARDIAC_EVENTS.index(testingObjs[sequenceIndex].getCardiacEvent())
        testingY[sequenceIndex, cardiacEventIndex] = 1

    return (trainingX, trainingY, testingX, testingY)
