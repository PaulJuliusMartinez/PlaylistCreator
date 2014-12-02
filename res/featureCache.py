import soundcloud
import json
import os
import sys
import numpy
import yaafelib as yaafe

class FeatureCache:
    def __init__(self):
        self.featureFile = 'songFeatures.json'
        self.features = {}
        self.loadFromFile()
        self.currentVersion = 1

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

    def saveToFile(self):
        with open(self.featureFile, 'w') as outfile:
            json.dump(self.features, outfile)

    def getFeature(self, songID):
        if songID in self.features:
            version = self.features[songID]['version']
            features = self.features[songID]['features']
            if version == self.currentVersion:
                return features

        return self.createNewEntry(songID)

    def createNewEntry(self, songID):
        print '/tracks/' + str(songID)
        track = self.client.get('/tracks/' + str(songID))
        print track
        print track.id
        self.features[songID] = {}
        self.features[songID]['version'] = self.currentVersion

        featureVector = {}
        # TODO: Add feature templates
        if hasattr(track, 'duration'):
            featureVector['duration'] = track.duration
        if hasattr(track, 'playback_count'):
            featureVector['playback_count'] = track.playback_count
        if hasattr(track, 'favorite_count'):
            featureVector['favorite_count'] = track.favorite_count
        if hasattr(track, 'download_count'):
            featureVector['download_count'] = track.download_count

        filename = './downloads/' + str(songID) + '.mp3'
        if not os.path.isfile(filename):
            url = track['permalink_url']
            os.system('python soundcloud-downloader.py ' + track['permalink_url'])

        self.afp.processFile(self.engine, filename)
        output = self.engine.readAllOutputs()
        featureVector['avgVolume'] = numpy.mean(output['loudness'])
        featureVector['beginVolume'] = numpy.mean(output['loudness'][:100])
        featureVector['endVolume'] = numpy.mean(output['loudness'][-100:])
        featureVector['maxVolume'] = numpy.percentile(output['loudness'], 90)
        featureVector['minVolume'] = numpy.percentile(output['loudness'], 10)
        featureVector['volumeVar'] = numpy.var(output['loudness'])
        featureVector['highFreq'] = numpy.percentile(output['maxfreq'], 90)
        featureVector['midFreq'] = numpy.percentile(output['maxfreq'], 50)
        featureVector['lowFreq'] = numpy.percentile(output['maxfreq'], 10)

        self.features[songID]['features'] = featureVector
        print featureVector

cache = FeatureCache()
cache.loadFromFile()
feature = cache.getFeature(32850380)
cache.saveToFile()

