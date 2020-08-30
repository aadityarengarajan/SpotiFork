from flask import redirect, render_template, Flask, request, url_for
from flask_session import Session
import startup,json,requests,secrets
from bs4 import BeautifulSoup #pip install html5lib


app = Flask(__name__)
app.secret_key = str(secrets.token_urlsafe(16))
app.config['SESSION_TYPE'] = 'filesystem'


Session(app)

@app.route('/')
def index():
    return render_template('enter.html')

    
@app.route('/login',methods=['POST','GET'])
def login():
    from flask import g,session
    if request.method == 'POST':
        userid=request.form['userlink']
        session['userid']=userid.replace('https://open.spotify.com/user/','').replace('/','')
    response = startup.getUser()
    return redirect(response)


@app.route('/callback/')
def callback(): 
    from flask import g,session
    startup.getUserToken(request.args['code'])
    return redirect(url_for('home',userid=session.get('userid')))

@app.route('/spotifork/<userid>')
def home(userid):
    from flask import g,session

    oauth = startup.getAccessToken()[1]['Authorization']
    session['oauth']=oauth
    data = {"Accept": "application/json",
    "Content-Type": "application/json", 
    "Authorization": session.get('oauth')}

    with requests.Session() as req:
        name = json.loads((BeautifulSoup((req.get(f'https://api.spotify.com/v1/users/{userid}',headers=data)).content, 'html5lib').body.prettify().replace('<body>','').replace('</body>','')))["display_name"]
    session['name']=name
    return render_template('getplaylist.html',session=session)

@app.route('/spotifork/fork',methods=['POST','GET'])
def fork():
    from flask import g,session
    playlist=request.form['playlistlink']

    playlistname=playlist.replace('https://open.spotify.com/playlist/','').replace('/','')
    session['playlistid']=playlistname
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': session.get('oauth')
    }

    params = (
        ('market', 'ES'),
    )

    with requests.Session() as req:
        response = req.get(f'https://api.spotify.com/v1/playlists/{session.get("playlistid")}/tracks', headers=headers, params=params)
        apiresp = json.loads((BeautifulSoup((response).content,'html5lib')).body.prettify().replace('<body>','').replace('</body>',''))
        session['apirespstep1'] = apiresp
    tracks=[]
    for i in session.get('apirespstep1')['items']:
        tracks.append(i['track']['uri'])
    session['tracklist']=tracks

    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': session.get('oauth')
    }

    params = (
    ('market', 'ES'),
    )


    with requests.Session() as req:
        result = req.get(f'https://api.spotify.com/v1/playlists/{session.get("playlistid")}', headers=headers, params=params)
        apiresp = json.loads((BeautifulSoup((result).content,'html5lib')).body.prettify().replace('<body>','').replace('</body>',''))
        session['apirespstep2'] = apiresp
    title=session.get('apirespstep2')['name']
    desc=session.get('apirespstep2')['description']
    session['title']=title
    session['description']=desc

    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': session.get('oauth'),
    }

    data = json.dumps({"name":f"Fork of {session.get('title')}","description":f"{session.get('description')}","public":'false'})

    with requests.Session() as req:
        result = req.post(f'https://api.spotify.com/v1/users/{session.get("name")}/playlists', headers=headers, data=data)
        apiresp = json.loads((BeautifulSoup((result).content,'html5lib')).body.prettify().replace('<body>','').replace('</body>',''))
        session['apirespstep3'] = apiresp
    
    newplayname=session.get('apirespstep3')['uri'].replace('"spotify:playlist:','')
    session['newplayname']=newplayname


    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': session.get('oauth')
    }
    
    with requests.Session() as req:
        req.post(f'https://api.spotify.com/v1/playlists/{session.get("newplayname").replace("spotify:playlist:","")}/tracks?uris={(",".join(session.get("tracklist"))).replace(":","%3A").replace(",","%2C")}', headers=headers)

    return render_template('completed.html',session=session)


if __name__ == "__main__": 
	app.run(port=5001)