import featureCache
import random
import json
import numpy as np
from util import *

def main():
  playlists = loadPlaylists()
  train = playlists[:8]
  validation = playlists[10:20]
  test = playlists[20:30]

  # Results: Map from partition string to (weightVector, trainScore, validationScore)
  results = {}

  numAssignments = 1
  for _ in range(numAssignments):
    assignment = generateNewAssignment(results, len(train))
    print assignment
    labeledData = labelData(train, assignment)
    classifier = MultiLinearClassifier()
    classifier.trainModel(labeledData, len(train))
    trainScore = classifier.testModel(train)
    #validationScore = classifier.testModel(validation)
    #print assignment, trainScore, validationScore
    #results[assignment] = (classifier.weights, trainScore, validationScore)

def loadPlaylists():
    return json.load(open('playlistPairs.json'))

def generateNewAssignment(oldAssignments, count):
  while True:
    assignment = ''.join(random.choice('01') for _ in range(count))
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

    """
    # Simple predictor
    def predictor(songID, playlistNum):
      score = dotProduct(self.weights, extractFeature(songID, playlistNum))
      if (score > 0): return 1
      return -1

    # Evaluate crude predictor progress
    def evaluatePredictor(examples, predictorFn):
      error = 0
      for song, playlist, score in examples:
        if predictorFn(song, playlist) != score:
          error += 1
      return 1.0 * error / len(examples)

    numIters = 30
    eta = 0.001
    for l in xrange(numIters):
      print "Train Error: ", evaluatePredictor(data, predictor)
      random.shuffle(data)
      for songID, playlistNum, score in data:
        features = extractFeature(songID, playlistNum)
        margin = dotProduct(self.weights, features) * score
        #print songID, playlistNum, score, dotProduct(self.weights, features)
        if (margin < 1):
          increment(self.weights, eta * score, features)
    for key in self.weights: print '\t', key, self.weights[key]
    """

    #
    A = np.zeros((len(data), 13 + numPlaylists))
    Y = np.zeros((len(data), 1))
    fs = featureCache.featureOrder
    for i, pack in enumerate(data):
      songID, playlistNum, score = pack
      Y[i] = score
      features = extractFeature(songID, playlistNum)
      for j, key in enumerate(fs):
        A[i][j] = features[key]
      for j in range(numPlaylists):
        A[i][len(fs) + j] = features['PLAYLIST_ORIGIN' + str(j)]

    A = np.matrix(A)
    Y = np.matrix(Y)

    self.weights = np.linalg.inv(np.matrix.transpose(A) * A) * np.matrix.transpose(A) * Y

    self.weights = self.weights[:len(fs)]
    asCounter = Counter({})
    for i, feature in enumerate(fs):
      asCounter[feature] = self.weights.item(i)
    self.weights = asCounter


  def testModel(self, validatedData):
    for playlist in validatedData:
      songs = playlist[0] + playlist[1]
      scores = []
      for song in songs:
        scores.append((dotProduct(self.weights, cache.getFeature(song)), song))
      scores.sort()

      countDiffs(playlist, [x[1] for x in scores])

    return 0


# Save and Load cache
cache = featureCache.FeatureCache()
#try:
if __name__ == "__main__":
  main()
cache.saveToFile()
#except:
#  print 'saving to file'
#  cache.saveToFile()
