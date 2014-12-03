import soundcloud

client = soundcloud.Client(client_id="94931d15df645c93103e0cd600377922")
track = client.get('/tracks/169850810')
print track

print track.id
print track.title
