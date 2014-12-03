import soundcloud
from featureCache import FeatureCache

class KMeansExploreClassifier:
	def __init__(self):
		self.featureCache = FeatureCache()
		self.weights = {}
		self.centroids = {}
		self.initializeWeights()

	def dot(weights, feature):
		result = 0
		for key, value in feature:
			result += weights[key] * value
		return result

	def weightedDistance(point1, point2, weights):
		result = 0
		for key in point1:
			result += weights[key] * (point1[key] - point2[key])**2
		return result

	def initializeWeights(self):
		exampleFeature = self.featureCache.getFeature(32850380)

		for key, value in exampleFeature:
			self.weights[key] = random.uniform(0, 10)

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
			dist1 = weightedDistance(self.featureCache.getFeature(song), centroids[0], self.weights)
			dist2 = weightedDistance(self.featureCache.getFeature(song), centroids[1], self.weights)
			if dist1 < dist2: playlists[0].append(song)
			else: playlists[1].append(song)
		return playlists

	def updateCentroids(self, centroids, playlists):
		for i in xrange(playlists):
			for song in playlists[i]:
				feature = self.featureCache.getFeature(song)
				centroids[i] = {}
				for key in feature:
					toAdd = 1/len(playlists[i]) * feature[key]
					if key in centroids[i]: centroids[i][key] += toAdd
					else: centroids[i][key] = toAdd

	def loss(self, testPlaylists, correctPlaylists):
		for playlist in correctPlaylists:
			songCheck = playlist[0]
			playlistCheck = []
			if songCheck in testPlaylists[0]: playlistCheck = testPlaylists[0]
			else: playlistCheck = testPlaylists[1]
			for song in playlist:
				

	def trainWeights(self, trainingPlaylistPairs):

		for trainPair in trainingPlaylistPairs:
			songs = []
			for song in trainPair[0]:
				songs.append(song)
			for song in trainPair[1]:
				songs.append(song)

			initializeCentroids(songs)
			playlists = assignSongs(self.centroids, songs)
			updateCentroids(self.centroids, playlists)


classifier = ExploreClassifier()