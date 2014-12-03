import soundcloud
from featureCache import FeatureCache
from util import *
from collections import Counter
import random
import copy

class KMeansExploreClassifier:
	def __init__(self):
		self.featureCache = FeatureCache()
		self.beamSize = 3
		self.bestWeights = []
		self.centroids = [Counter(), Counter()]
		self.initializeWeights()

	def weightedDistance(self, weights, point1, point2):
		result = 0
		for key in point1:
			result += weights.get(key) * (point1.get(key, 0) - point2.get(key, 0))**2
		return result

	def initializeWeights(self):
		exampleFeature = self.featureCache.getFeature(33387088)
		for i in range(self.beamSize):
			weights = Counter();
			for key, value in exampleFeature.iteritems():
				weights[key] = 1
			self.bestWeights.append(weights)

	def initializeCentroids(self, songs):
		randomIndex1 = random.randint(0, len(songs)-1)
		randomIndex2 = random.randint(0, len(songs)-1)
		while randomIndex2 == randomIndex1:
			randomIndex2 = random.randint(0, len(songs)-1)
		self.centroids[0] = self.featureCache.getFeature(songs[randomIndex1])
		self.centroids[1] = self.featureCache.getFeature(songs[randomIndex2])

	def assignSongs(self, weights, songs):
		playlists = [[],[]]
		for song in songs:
			dist1 = self.weightedDistance(weights, self.featureCache.getFeature(song), self.centroids[0])
			dist2 = self.weightedDistance(weights, self.featureCache.getFeature(song), self.centroids[1])
			if dist1 < dist2: playlists[0].append(song)
			else: playlists[1].append(song)
		return playlists

	def updateCentroids(self, playlists):
		for i in xrange(len(playlists)):
			self.centroids[i] = Counter()
			for song in playlists[i]:
				feature = self.featureCache.getFeature(song)
				for key in feature:
					toAdd = float(1)/len(playlists[i]) * feature[key]
					self.centroids[i][key] = self.centroids[i].get(key, 0) + toAdd

	#number of songs that aren't in test that should be
	def playlistDiff(self, test, correct):
		result = 0
		for song in correct:
			if song not in test: result += 1
		return result


	def loss(self, test, correct):
		return min(self.playlistDiff(test[0], correct[0]) + self.playlistDiff(test[1], correct[1]), \
			self.playlistDiff(test[0], correct[1]) + self.playlistDiff(test[1], correct[0]))

	def generatePossibleDirections(self):
		possibleDirections = []
		numNewDirections = 20
		for i in xrange(numNewDirections):
			newDirection = Counter()
			for key in self.bestWeights[0]:
				newDirection[key] = max(random.uniform(-0.25, 0.25), 0)
			possibleDirections.append(newDirection)
		noMovement = Counter()
		for key in self.bestWeights[0]:
			noMovement[key] = 0
		possibleDirections.append(noMovement)
		return possibleDirections

	def cluster(self, weights, songs):
		numIters = 20
		self.initializeCentroids(songs)
		for i in xrange(numIters):
			if self.centroids[0] == self.centroids[1]: print "ERROR: CENTROIDS ARE THE SAME"
			playlists = self.assignSongs(weights, songs)
			self.updateCentroids(playlists)
		return playlists

	def train(self, trainingPlaylistPairs):
		totalLoss = 0
		count = 0
		numIters = 20
		eta = 0.1
		for trainPair in trainingPlaylistPairs:
			count += 1
			songs = trainPair[0] + trainPair[1]

			bestLosses = [500] * self.beamSize
			bestWeights = [Counter()] * self.beamSize
			for _ in xrange(numIters):
				possibleDirections = self.generatePossibleDirections()
				

				for weights in copy.deepcopy(self.bestWeights):
					for i in xrange(len(possibleDirections)):
						currentWeights = weights + possibleDirections[i]
						playlists = self.cluster(currentWeights, songs)
						loss = self.loss(playlists, trainPair)
						if loss < max(bestLosses): 
							for index in range(self.beamSize):
								if loss < bestLosses[index]:
									bestLosses[index] = loss
									newBestWeight = Counter()
									for key in weights:
										newBestWeight[key] = weights[key] + eta * possibleDirections[i][key]
									bestWeights[index] = newBestWeight
				self.bestWeights = bestWeights

			totalLoss += float(bestLosses[0]) / len(songs)
			print "Average Training Loss:", totalLoss / count

	def test(self, testingPlaylistPairs):
		totalLoss = 0
		count = 0
		for testPair in testingPlaylistPairs:
			count += 1
			songs = testPair[0] + testPair[1]
			playlists = self.cluster(self.bestWeights[0], songs)

			loss = self.loss(playlists, testPair)
			totalLoss += float(loss) / len(songs)
			print "Average Testing Loss:", totalLoss / count

def randomAssignPlaylists(songs):
	playlists = [[],[]]
	for song in songs:
		playlists[random.randint(0,1)].append(song)
	return playlists

def randomAssignmentTest(classifier, testingPlaylistPairs):
	totalLoss = 0
	count = 0
	for testPair in testingPlaylistPairs:
		count += 1
		songs = testPair[0] + testPair[1]
		playlists = randomAssignPlaylists(songs)

		loss = classifier.loss(playlists, testPair)
		totalLoss += float(loss) / len(songs)
		print "Average Random Loss:", totalLoss / count


random.seed()
classifier = KMeansExploreClassifier()
playlists = loadPlaylists()
train = playlists[:20]
test = playlists[20:30]
classifier.train(train)
classifier.test(test)
randomAssignmentTest(classifier, test)

