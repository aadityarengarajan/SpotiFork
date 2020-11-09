from flask_spotify_auth import getAuth, refreshAuth, getToken

CLIENT_ID = "4bc7d69d58a74c639d6d7f3b3f664809"
CLIENT_SECRET = "0dceacbf02d542aa8f23934752b3501c"
PORT = "5000"
CALLBACK_URL = "http://localhost"
SCOPE = "streaming playlist-modify-public user-read-private playlist-read-private playlist-read-collaborative playlist-modify-private"
TOKEN_DATA = []


def getUser():
    return getAuth(CLIENT_ID, "{}:{}/callback/".format(CALLBACK_URL, PORT), SCOPE)

def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET, f"{CALLBACK_URL}:{PORT}/callback/")
 
def refreshToken(time):
    time.sleep(time)
    TOKEN_DATA = refreshAuth()

def getAccessToken():
    return TOKEN_DATA