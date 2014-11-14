import soundcloud
import json

json_data = open("../res/data.json")
data = json.load(json_data)

client = soundcloud.Client(client_id="94931d15df645c93103e0cd600377922")

def getPlaylist(urlstring):
	playlist = client.get('/resolve', url=urlstring)
	tracks = playlist.tracks
	data[playlist.title] = {}
	for track in playlist.tracks:
		print track
		print '==========================='
		featureVector = {}

		featureVector["title"] = track['title']
		featureVector["duration"] = track['duration']
		featureVector["genre"] = track['genre']
		featureVector["year"] = track['release_year']
		featureVector["type"] = track['track_type']
		featureVector["bpm"] = track['bpm']
		featureVector["key_signature"] = track['key_signature']
		# featureVector["plays"] = track['playback_count']
		# featureVector["favorites"] = track['favoritings_count']
		# featureVector["downloads"] = track['download_count']
		featureVector["tags"] = track['tag_list']

		data[playlist.title][track['title']] = featureVector


getPlaylist('https://soundcloud.com/calstud/sets/ski-dock')
getPlaylist('https://soundcloud.com/calstud/sets/tom-misch')

# track = client.get('/resolve', url='https://soundcloud.com/toddterje/todd-terje-inspector-norse')



	# print featureVector

with open('../res/data.json', 'w') as outfile:
  json.dump(data, outfile)
print data


