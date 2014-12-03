import soundcloud
import json
import os
import sys
import numpy
import math
import yaafelib as yaafe
from collections import Counter

class FeatureCache:
    def __init__(self):
        self.featureFile = 'songFeatures.json'
        self.features = {}
        self.currentVersion = 5
        self.loadFromFile()

        # Initialize soundcloud connection
        self.client = soundcloud.Client(client_id="94931d15df645c93103e0cd600377922")

        # Define the features plan
        self.fp = yaafe.FeaturePlan(sample_rate=44100, normalize=None, resample=True)
        self.fp.loadFeaturePlan('featureplan')

        # Initialize yaafe engine
        self.engine = yaafe.Engine()
        if not self.engine.load(self.fp.getDataFlow()):
            print 'MAJOR ERROR: YAAFE FAILED TO LOAD'
            sys.exit()
        # Initialize file processor
        self.afp = yaafe.AudioFileProcessor()


    def loadFromFile(self):
        self.features = json.load(open(self.featureFile))
        # Convert everything to a Counter
        for key in self.features:
          if u'features' in self.features[key]:
            self.features[key][u'features'] = Counter(self.features[key][u'features'])

    def saveToFile(self):
        for key in self.features:
            for i in range(100): del self.features[key][u'features']['PLAYLIST_ORIGIN' + str(i)]
        with open(self.featureFile, 'w') as outfile:
            outfile.truncate()
            json.dump(self.features, outfile)

    def getFeature(self, songID):
        songID = unicode(str(songID))
        if songID in self.features:
            version = self.features[songID][u'version']
            if u'features' in self.features[songID]:
              features = self.features[songID][u'features']
              if version == self.currentVersion:
                  return features

        # print 'Creating New Feature for Song: ', songID
        return self.createNewEntry(songID)

    def createNewEntry(self, songID):
        track = self.client.get('/tracks/' + str(songID))
        self.features[songID] = {}
        self.features[songID][u'version'] = self.currentVersion

        featureVector = {}
        # TODO: Add feature templates
        if hasattr(track, u'duration'):
            featureVector[u'duration'] = track.duration / 1000
        if hasattr(track, u'playback_count'):
            featureVector[u'playback_count'] = math.log(track.playback_count + 1)
        if hasattr(track, u'favoritings_count'):
            featureVector[u'favoritings_count'] = math.log(track.favoritings_count + 1)
        if hasattr(track, u'download_count'):
            featureVector[u'download_count'] = math.log(track.download_count + 1)

        filename = './downloads/' + str(songID) + '.mp3'
        if not os.path.isfile(filename):
            os.system('python soundcloud-downloader.py ' + track.permalink_url)

        self.afp.processFile(self.engine, filename)
        output = self.engine.readAllOutputs()
        featureVector[u'avgVolume'] = numpy.mean(output['loudness'])
        featureVector[u'beginVolume'] = numpy.mean(output['loudness'][:100])
        featureVector[u'endVolume'] = numpy.mean(output['loudness'][-100:])
        featureVector[u'maxVolume'] = numpy.percentile(output['loudness'], 90)
        featureVector[u'minVolume'] = numpy.percentile(output['loudness'], 10)
        featureVector[u'volumeVar'] = numpy.var(output['loudness'])
        featureVector[u'highFreq'] = math.log(numpy.percentile(output['maxfreq'], 90))
        featureVector[u'midFreq'] = math.log(numpy.percentile(output['maxfreq'], 50))
        featureVector[u'lowFreq'] = math.log(numpy.percentile(output['maxfreq'], 10))

        self.features[songID][u'features'] = Counter(featureVector)

        return self.features[songID][u'features']

featureOrder = [
  u'duration',
  u'playback_count',
  u'favoritings_count',
  u'download_count',
  u'avgVolume',
  u'beginVolume',
  u'endVolume',
  u'maxVolume',
  u'minVolume',
  u'volumeVar',
  u'highFreq',
  u'midFreq',
  u'lowFreq'
]


