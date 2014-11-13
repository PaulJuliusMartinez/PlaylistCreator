import soundcloud

client = soundcloud.Client(client_id="94931d15df645c93103e0cd600377922")

track = client.get('/resolve', url='https://soundcloud.com/toddterje/todd-terje-inspector-norse')

print track.id
