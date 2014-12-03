import featureCache
import random
import json
import numpy as np
from util import *

def main():
  s = 0.0
  l = 50
  for _ in range(900):
    a = [range(l / 2), range(l / 2, l)]
    b = range(l)
    random.shuffle(b)
    s += countDiffs(a, b) / (float(l) / 2.0)
  print s / 900.0

  playlists = loadPlaylists()
  train = playlists[:80]
  validation1 = playlists[80:100]
  validation2 = playlists[100:120]
  test = playlists[120:]

  # Results: Map from partition string to (weightVector, trainScore, validationScore)
  results = {}

  numAssignments = 300
  best = MultiLinearClassifier()
  bestTestErr = 1
  totalTrainErr = 0
  totalValidationErr = 0
  for _ in range(numAssignments):
    assignment = generateNewAssignment(results, len(train))
    labeledData = labelData(train, assignment)
    classifier = MultiLinearClassifier()
    classifier.trainModel(labeledData, len(train))
    trainScore = classifier.testModel(train)
    validationScore1 = classifier.testModel(validation1)
    validationScore2 = classifier.testModel(validation2)
    testScore = classifier.testModel(test)
    totalTrainErr += trainScore
    totalValidationErr += validationScore1
    if (validationScore1 < bestTestErr):
      bestTestErr = validationScore1
      best = classifier
    print '{0} {1};'.format(validationScore1, validationScore2)
    results[assignment] = (classifier.weights, trainScore, validationScore1)

  print bestTestErr
  print best.testModel(test)
  print 'avg train:', totalTrainErr / float(numAssignments)
  print 'avg validation:', totalValidationErr / float(numAssignments)

def generateNewAssignment(oldAssignments, count):
  while True:
    assignment = '1' + ''.join(random.choice('01') for _ in range(count - 1))
    if not assignment in oldAssignments:
      return assignment

# Takes the list of playlist divisions and returns a list of tuples:
# (SongID, OriginalPlaylist, Score (-1 or 1))
def labelData(data, assignment):
  labeledData = []
  for i, playlist in enumerate(data):
    # If assignment is 0, assignment, songs in playlist[0] are positve,
    # songs in playlist[1] are negative
    for song in playlist[0]:
      labeledData.append( (song, i, -2 * int(assignment[i]) + 1) )
    for song in playlist[1]:
      labeledData.append( (song, i, 2 * int(assignment[i]) - 1) )
  return labeledData


class MultiLinearClassifier:
  def __init__(self):
    self.weights = {}

  # Trains a model on the data
  def trainModel(self, data, numPlaylists):

    # Add constant feature depending on which playlist it came from
    def extractFeature(songID, playlistNum):
      f = cache.getFeature(songID)
      for i in range(2):
        if i == playlistNum:
          f['PLAYLIST_ORIGIN' + str(i)] = 1
        else:
          f['PLAYLIST_ORIGIN' + str(i)] = 0
      return f

#    # Simple predictor
#    def predictor(songID, playlistNum):
#      score = dotProduct(self.weights, extractFeature(songID, playlistNum))
#      if (score > 0): return 1
#      return -1
#
#    # Evaluate crude predictor progress
#    def evaluatePredictor(examples, predictorFn):
#      error = 0
#      for song, playlist, score in examples:
#        if predictorFn(song, playlist) != score:
#          error += 1
#      return 1.0 * error / len(examples)
#
#    numIters = 30
#    eta = 0.001
#    for l in xrange(numIters):
#      print "Train Error: ", evaluatePredictor(data, predictor)
#      random.shuffle(data)
#      for songID, playlistNum, score in data:
#        features = extractFeature(songID, playlistNum)
#        margin = dotProduct(self.weights, features) * score
#        #print songID, playlistNum, score, dotProduct(self.weights, features)
#        if (margin < 1):
#          increment(self.weights, eta * score, features)
#    for key in self.weights: print '\t', key, self.weights[key]

    fs = featureCache.featureOrder
    A = np.zeros((len(data), len(fs) + numPlaylists))
    Y = np.zeros((len(data), 1))
    for i, pack in enumerate(data):
      songID, playlistNum, score = pack
      Y[i] = score
      features = extractFeature(songID, playlistNum)
      for j, key in enumerate(fs):
        A[i][j] = features[key]
      for j in range(numPlaylists):
        A[i][len(fs) + j] = 1 if j == playlistNum else 0

    A = np.matrix(A)
    Y = np.matrix(Y)

    self.weights = np.linalg.inv(np.matrix.transpose(A) * A) * np.matrix.transpose(A) * Y

    self.weights = self.weights[:len(fs)]
    asCounter = Counter({})
    for i, feature in enumerate(fs):
      asCounter[feature] = self.weights.item(i)
    self.weights = asCounter


  def testModel(self, validatedData):
    err = 0
    for playlist in validatedData:
      songs = playlist[0] + playlist[1]
      scores = []
      for song in songs:
        scores.append((dotProduct(self.weights, cache.getFeature(song)), song))
      scores.sort()

      err += countDiffs(playlist, [x[1] for x in scores]) / float(len(playlist[0]))

    return err / len(validatedData)


# Save and Load cache
cache = featureCache.FeatureCache()
#try:
if __name__ == "__main__":
  main()
cache.saveToFile()
#except:
#  print 'saving to file'
#  cache.saveToFile()
