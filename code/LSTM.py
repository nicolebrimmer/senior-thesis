'''
        This file includes all of the methods required to create, train and test the LSTM model
        that is used to predict episodes of VT.

        Adapted from: https://github.com/aurotripathy/lstm-ecg-wave-anomaly-detect/blob/master/lstm-ecg-wave-anomaly-detect.py
'''

from readData import CARDIAC_EVENTS, TYPES_OF_EVENTS_DICT
import numpy as np

from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.optimizers import SGD

# Hyperparameters
# batch_size = 32:
epoch = 10

def createModel(numOfBeats, numOfReadings, numOfOutcomes):
        '''
                Creates, compiles and returns an LSTM model that can be used to predict episodes of VT.
        '''

        model = Sequential()

        model.add(LSTM(32, input_shape=(numOfBeats, numOfReadings), return_sequences=True))
        model.add(Dropout(0.2))

        model.add(LSTM(32, return_sequences=True))
        model.add(Dropout(0.2))

        model.add(LSTM(32, return_sequences=False))
        model.add(Dropout(0.2))

        model.add(Dense(numOfOutcomes))
        model.add(Activation('softmax'))

        sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer='adam')
        return model

def evaluateModel(rawPredictedY, rawActualY, verboseFile):
    
    '''
        Evaluates a LSTM model that can be used to predict episodes of VT.
        
        Returns a tuple of the form ([sensitivity], [specificity]) where [sensitivity] is the sensitivity
        of the model's ability to predict episodes of VT and [specificity] is the specificity of the model's
        ability to predict episodes of VT.
    
    '''
    
    (numOfTesting, numOfOutcomes) = np.shape(rawActualY)
    
    # Convert probabilities in rawPredictedY into classifications.
    predictedY = np.zeros((numOfTesting, 1), dtype=np.int16)
    for testingIndex in range(numOfTesting):
        
        maxVal = 0
        maxOutcomeIndex = 0
        for outcomeIndex in range(numOfOutcomes):
            val = rawPredictedY[testingIndex, outcomeIndex]
            if (val > maxVal):
                maxVal = val
                maxOutcomeIndex = outcomeIndex
        
        predictedY[testingIndex, 0] = maxOutcomeIndex

    # Convert binary things in rawPredictedY into classficiations.
    actualY = np.zeros((numOfTesting, 1), dtype=np.int16)
    for testingIndex in range(numOfTesting):
        for outcomeIndex in range(numOfOutcomes):
            if (rawActualY[testingIndex, outcomeIndex] == 1):
                actualY[testingIndex, 0] = outcomeIndex

    # Set up dictionaries that keep track of the actual and predicted numbers
    # of each cardiac event.
    numOfEachAuxPredicted = {}
    numOfEachAuxActual = {}
    for aux in TYPES_OF_EVENTS_DICT:
        numOfEachAuxPredicted[aux] = 0
        numOfEachAuxActual[aux] = 0

    # Compute entries in dictionaries that keep track of the actual and predicted
    # numbers of each cardiac event.
    for index in range(numOfTesting):
        predictedAux = CARDIAC_EVENTS[predictedY[index, 0]]
        actualAux = CARDIAC_EVENTS[actualY[index, 0]]
            
        numOfEachAuxPredicted[predictedAux] = numOfEachAuxPredicted[predictedAux] + 1
        numOfEachAuxActual[actualAux] = numOfEachAuxActual[actualAux] + 1

    # Print entries in dictionaries that keep track of the actual and predicted
    # numbers of each cardiac event.
    for aux in TYPES_OF_EVENTS_DICT:
        verboseFile.write('Cardiac Event: ' + str(TYPES_OF_EVENTS_DICT[aux]) + '\n')
        verboseFile.write('\tActual: ' + str(numOfEachAuxActual[aux]) + '\n')
        verboseFile.write('\tPredicted: ' + str(numOfEachAuxPredicted[aux]) + '\n')
        verboseFile.write('')

    # Calculate specificity and sensitivity.
    tn = 0
    n = 0
    tp = 0
    p = 0
    numOfCorrect = 0

    numForVT = CARDIAC_EVENTS.index('(VT')
    for i in range(numOfTesting):
        
        if (actualY[i, 0] == predictedY[i, 0]):
            numOfCorrect = numOfCorrect + 1
            
        # Positives
        if (actualY[i, 0] == numForVT):
            p = p + 1
                    
            # True positives
            if (predictedY[i, 0] == numForVT):
                tp = tp + 1
        
        # Negatives
        else:
            n = n + 1
                    
            # True negatives
            if (predictedY[i, 0] != numForVT):
                tn = tn + 1

    verboseFile.write('Num of positives: ' + str(p) + '\n')
    verboseFile.write('Num of negatives: ' + str(n) + '\n')
    verboseFile.write('Num of true positives: ' + str(tp) + '\n')
    verboseFile.write('Num of true negatives: ' + str(tn) + '\n')

    verboseFile.write('Num of correct: ' + str(numOfCorrect) + '\n')

    if (p == 0):
        sensitivity = -1
    else:
        sensitivity = float(tp) / float(p)

    if (n == 0):
        specificity = -1
    else:
        specificity = float(tn) / float(n)

    verboseFile.write("Sensitivity: " + str(sensitivity) + '\n')
    verboseFile.write("Specificity: " + str(specificity) + '\n')
    verboseFile.write('\n\n')    

    return (sensitivity, specificity)

def runModel(trainingX, trainingY, testingX, testingY, verboseFile):
    '''
        Creates, trains and evaluates an LSTM model that can be used to predict episodes of VT.
        
        Returns a tuple of the form ([sensitivity], [specificity]) where [sensitivity] is the sensitivity
        of the model's ability to predict episodes of VT and [specificity] is the specificity of the model's
        ability to predict episodes of VT.
    
    '''
    
    # Create the LSTM model.
    print ("Creating...")
    numOfOutcomes = len(CARDIAC_EVENTS)

    for cardiacEvent in CARDIAC_EVENTS:
         print (cardiacEvent)    

    (numOfSequences, numOfBeats, numOfReadings) = trainingX.shape	
    model = createModel(numOfBeats, numOfReadings, numOfOutcomes)
    print ("Completed!")

    # Train the LSTM model.
    print ("Training...")
    model.fit(x = trainingX, y = trainingY, nb_epoch = epoch, validation_split = 0.05)
    print ("Completed!")

    # Evaluate the LSTM model.
    print ("Evaluating...")
    rawPredictedY = model.predict(testingX)
    
    for outcome in range(numOfOutcomes):
          print rawPredictedY[0, outcome]
    (sensitivity, specificity) = evaluateModel(rawPredictedY, testingY, verboseFile)
    print ("Completed!")

    return (sensitivity, specificity)
