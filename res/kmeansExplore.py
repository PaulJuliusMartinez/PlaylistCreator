import soundcloud
from featureCache import FeatureCache
from util import *
from collections import Counter
import random

class KMeansExploreClassifier:
	def __init__(self):
		self.featureCache = FeatureCache()
		self.weights = Counter()
		self.centroids = {}
		self.initializeWeights()

	def weightedDistance(self, point1, point2):
		result = 0
		for key in point1:
			result += self.weights.get(key, 0) * (point1.get(key, 0) - point2.get(key, 0))**2
		return result

	def initializeWeights(self):
		exampleFeature = self.featureCache.getFeature(103281373)
		for key, value in exampleFeature.iteritems():
			self.weights[key] = random.uniform(0, 3)

	def initializeCentroids(self, songs):
		randomIndex1 = random.randint(0, len(songs)-1)
		randomIndex2 = random.randint(0, len(songs)-1)
		while randomIndex2 == randomIndex1:
			randomIndex2 = random.randint(0, len(songs)-1)
		self.centroids[0] = self.featureCache.getFeature(songs[randomIndex1])
		self.centroids[1] = self.featureCache.getFeature(songs[randomIndex2])

	def assignSongs(self, centroids, songs):
		playlists = [[],[]]
		for song in songs:
			dist1 = self.weightedDistance(self.featureCache.getFeature(song), centroids[0])
			dist2 = self.weightedDistance(self.featureCache.getFeature(song), centroids[1])
			if dist1 < dist2: playlists[0].append(song)
			else: playlists[1].append(song)
		return playlists

	def updateCentroids(self, centroids, playlists):
		for i in xrange(len(playlists)):
			for song in playlists[i]:
				feature = self.featureCache.getFeature(song)
				centroids[i] = {}
				for key in feature:
					toAdd = 1/len(playlists[i]) * feature[key]
					centroids[i][key] = centroids[i].get(key, 0) + toAdd

	#number of songs that aren't in test that should be
	def playlistDiff(self, test, correct):
		result = 0
		for song in correct:
			if song not in test: result += 1
		return result


	def loss(self, test, correct):
		return min(self.playlistDiff(test[0], correct[0]) + self.playlistDiff(test[1], correct[1]), \
			self.playlistDiff(test[0], correct[1]) + self.playlistDiff(test[1], correct[0]))

	def generateNewWeights(self):
		possibleWeights = []
		numNewWeights = 10
		for i in xrange(10):
			newWeights = {}
			for key in self.weights:
				newWeights[key] = max(self.weights[key] + random.uniform(-1, 1), 0)
			possibleWeights.append(newWeights)
		return possibleWeights

	def cluster(self, songs):
		numIters = 10
		self.initializeCentroids(songs)			
		for i in xrange(numIters):
			playlists = self.assignSongs(self.centroids, songs)
			self.updateCentroids(self.centroids, playlists)
		return playlists

	def train(self, trainingPlaylistPairs):
		for trainPair in trainingPlaylistPairs:
			songs = []
			for song in trainPair[0]: 
				songs.append(song)
			for song in trainPair[1]:
				songs.append(song)

			possibleWeights = self.generateNewWeights()
			bestLoss = 0
			bestWeights = 0
			for i in xrange(len(possibleWeights)):
				self.weights = possibleWeights[i]
				playlists = self.cluster(songs)
				loss = self.loss(playlists, trainPair)
				if i == 0 or loss < bestLoss: 
					bestLoss = loss
					bestWeights = i
			self.weights = possibleWeights[bestWeights]
			print "TRAIN LOSS:", bestLoss

	def test(self, testingPlaylistPairs):
		for testPair in testingPlaylistPairs:
			songs = []
			for song in testPair[0]: 
				songs.append(song)
			for song in testPair[1]:
				songs.append(song)
			playlists = self.cluster(songs)

			print "Playlist1 Size:", len(playlists[0]), "Playlist2 Size:", len(playlists[1])
			print "Correct1 Size:", len(testPair[0]), "Correct2 Size:", len(testPair[1])
			print "TEST LOSS:", self.loss(playlists, testPair)

classifier = KMeansExploreClassifier()
playlists = loadPlaylists()
train = playlists[:20]
test = playlists[20:30]
classifier.train(train)
classifier.test(test)

