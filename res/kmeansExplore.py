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
		playlistLength = len(songs) / 2
		for song in songs:
			dist1 = self.weightedDistance(weights, self.featureCache.getFeature(song), self.centroids[0])
			dist2 = self.weightedDistance(weights, self.featureCache.getFeature(song), self.centroids[1])
			if dist1 < dist2: 
				if len(playlists[0]) < playlistLength: playlists[0].append((dist1, song))
				elif dist1 < min(playlists[0]):
					toSwap = max(playlists[0])
					playlist[0].remove(toSwap)
					newDistance = self.weightedDistance(weights, self.featureCache.getFeature(toSwap[1]), self.centroids[1])
					playlists[1].append((newDistance, toSwap[1]))
				else: playlists[1].append((dist2, song))
			else: 
				if len(playlists[1]) < playlistLength: playlists[1].append((dist2, song))
				elif dist2 < min(playlists[1]):
					toSwap = max(playlists[1])
					playlist[1].remove(toSwap)
					newDistance = self.weightedDistance(weights, sef.featureCache.getFeature(toSwap[1]), self.centroids[0])
					playlsts[0].append(newDistance, toSwap[1])
				else: playlists[0].append((dist1, song))
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
		numNewDirections = 40
		for i in xrange(numNewDirections):
			newDirection = Counter()
			for key in self.bestWeights[0]:
				newDirection[key] = random.uniform(-0.5, 0.5)
			possibleDirections.append(newDirection)
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
		numIters = 10
		eta = 0.1
		bestLosses = [2] * self.beamSize
		bestWeights = [Counter()] * self.beamSize
		for _ in xrange(numIters):
			possibleDirections = self.generatePossibleDirections()
			for weights in copy.deepcopy(self.bestWeights):
				for i in xrange(len(possibleDirections)):
					totalLoss = 0
					currentWeights = weights + possibleDirections[i]

					for trainPair in trainingPlaylistPairs:
						songs = trainPair[0] + trainPair[1]
				
						playlists = self.cluster(currentWeights, songs)
						loss = self.loss(playlists, trainPair)
						totalLoss += float(loss) / len(songs)

					averageLoss = totalLoss / len(trainingPlaylistPairs)
					#update best weights
					for index in range(self.beamSize):
						if averageLoss < bestLosses[index]:
							print "UPDATING WEIGHTS!"
							bestLosses.insert(index, averageLoss)
							bestLosses.pop(self.beamSize)
							newBestWeight = Counter()
							for key in weights:
								newBestWeight[key] = max(weights[key] + eta * possibleDirections[i][key], 0)
							bestWeights.insert(index, newBestWeight)
							bestWeights.pop(self.beamSize)
							break
			self.bestWeights = bestWeights
			print "Average Training Loss:", bestLosses[0]

	def test(self, testingPlaylistPairs):
		totalLoss = 0
		count = 0
		for testPair in testingPlaylistPairs:
			count += 1
			songs = testPair[0] + testPair[1]
			playlists = self.cluster(self.bestWeights[0], songs)

			loss = self.loss(playlists, testPair)
			testLoss = float(loss) / len(songs)
			totalLoss += testLoss
			print "Test Loss:", testLoss
		print "Average Testing Loss:", totalLoss / len(testingPlaylistPairs)

	def validate(self, validationPlaylistPairs):
		totalLoss = 0
		count = 0
		for testPair in validationPlaylistPairs:
			count += 1
			songs = testPair[0] + testPair[1]
			playlists = self.cluster(self.bestWeights[0], songs)

			loss = self.loss(playlists, testPair)
			validationLoss = float(loss) / len(songs)
			totalLoss += validationLoss
			print "Validation Loss:", validationLoss
		print "Average Validation Loss:", totalLoss / len(validationPlaylistPairs)

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
		randomLoss = float(loss) / len(songs)
		totalLoss += randomLoss
		print "Random Loss:", randomLoss
	print "Average Random Loss:", totalLoss / len(testingPlaylistPairs)


random.seed()
classifier = KMeansExploreClassifier()
playlists = loadPlaylists()
train = playlists[:20]
validation = playlists[20:40]
validation2 = playlists[40:60]
test = playlists[60:100]
classifier.train(train)
classifier.validate(validation)
classifier.validate(validation2)
classifier.test(test)
randomAssignmentTest(classifier, test)

