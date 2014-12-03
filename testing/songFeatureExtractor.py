import soundcloud
import json

playlists = []
songContent = {}
playlistPairs = []

client = soundcloud.Client(client_id="94931d15df645c93103e0cd600377922")

# These are songs that can't be downloaded. Don't add them to playlists.
blacklist = [53433975, 169850810, 59051244, 76989671, 88606549, 75868018, 93555520, 44168358, 88078067, 98391174, 63424835, 124170847, 131827025, 64065407, 120911249]


def buildPlaylistPairs():
    currentPair = ()
    p1 = []
    p2 = []
    for i in xrange(len(playlists)):
        p1 = playlists[i][:]
        for j in xrange(i+1, len(playlists)):
            p2 = playlists[j][:]
            for song1 in playlists[i]:
                for song2 in playlists[j]:
                    if song1 == song2:
                        p1.remove(song1)
                        p2.remove(song1)
            l = min(len(p1), len(p2))
            currentPair = (p1[:l], p2[:l])
            playlistPairs.append(currentPair)

def addFeature(featureVec, track, featureName):
    if featureName in track:
        featureVec[featureName] = track[featureName]
    else:
        featureVec[featureName] = None

def getPlaylist(urlstring):
    playlist = client.get('/resolve', url=urlstring)
    tracks = playlist.tracks
    currentPlaylist = []
    print "Getting playlist:", playlist.title
    for track in playlist.tracks:

        # if not track['streamable']: 
        #     print "Skipping song", track['title'], "because it is not streamable"
        #     continue
        if track['id'] in blacklist:
            continue
        try:
            print track['id']
            client.get('/tracks/' + str(track['id']))
        except:
            print 'Track: ', track['id'], " couldn't be downloaded"
            continue

        if track['id'] in songContent: 
            print "Skipping song", track['title'], "because it has already been processed"
            continue

        featureVector = {}
        addFeature(featureVector, track, 'id')
        addFeature(featureVector, track, 'created_at')
        addFeature(featureVector, track, 'user')
        addFeature(featureVector, track, 'title')
        addFeature(featureVector, track, 'sharing')
        addFeature(featureVector, track, 'description')
        addFeature(featureVector, track, 'label_name')
        addFeature(featureVector, track, 'license')
        addFeature(featureVector, track, 'duration')
        addFeature(featureVector, track, 'genre')
        addFeature(featureVector, track, 'release_year')
        addFeature(featureVector, track, 'track_type')
        addFeature(featureVector, track, 'bpm')
        addFeature(featureVector, track, 'key_signature')
        addFeature(featureVector, track, 'comment_count')
        addFeature(featureVector, track, 'playback_count')
        addFeature(featureVector, track, 'favoritings_count')
        addFeature(featureVector, track, 'download_count')
        addFeature(featureVector, track, 'tag_list')


        #change to download the specific song using soundcloud-downloader.py and extract
        #features from it here
        fileLoc = "~/Desktop/playlists/" + playlist.title + "/" + str(track['id']) + ".mp3"
        featureVector['file_location'] = fileLoc

        songContent[track['id']] = featureVector
        currentPlaylist.append(track['id'])
    if len(currentPlaylist) == 0: return
    print "Saving playlist:", playlist.title
    playlists.append(currentPlaylist)


getPlaylist('https://soundcloud.com/calstud/sets/ski-dock')
getPlaylist('https://soundcloud.com/calstud/sets/tom-misch')
getPlaylist('https://soundcloud.com/calstud/sets/lemaitre')
getPlaylist('https://soundcloud.com/calstud/sets/pogo')
getPlaylist('https://soundcloud.com/zach-saraf/sets/dope')
getPlaylist('https://soundcloud.com/zach-saraf/sets/perchance')
getPlaylist('https://soundcloud.com/zach-saraf/sets/rap')
getPlaylist('https://soundcloud.com/zach-saraf/sets/spring')
getPlaylist('https://soundcloud.com/zach-saraf/sets/perchance-2')
getPlaylist('https://soundcloud.com/zach-saraf/sets/perchance-3')
getPlaylist('https://soundcloud.com/zach-saraf/sets/coachella-road-trip')
getPlaylist('https://soundcloud.com/franzwarning/sets/sunmusic')
getPlaylist('https://soundcloud.com/franzwarning/sets/sunset-parties')
getPlaylist('https://soundcloud.com/franzwarning/sets/of-late')
getPlaylist('https://soundcloud.com/franzwarning/sets/coachella-darties')
getPlaylist('https://soundcloud.com/pb-kjelly/sets/new-new-synthy-wunderland')
getPlaylist('https://soundcloud.com/pb-kjelly/sets/bish-dont-kill-my-vibe')
getPlaylist('https://soundcloud.com/pb-kjelly/sets/chilled-out')

buildPlaylistPairs()

# track = client.get('/resolve', url='https://soundcloud.com/toddterje/todd-terje-inspector-norse')

#with open('res/playlists.json', 'w') as outfile:
#  json.dump(playlists, outfile)
#with open('res/songContent.json', 'w') as outfile:
#  json.dump(songContent, outfile)
with open('res/playlistPairs.json', 'w') as outfile:
  json.dump(playlistPairs, outfile)


