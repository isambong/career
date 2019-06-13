
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os
import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)
from bs4 import BeautifulSoup
import json
import re
app = Flask(__name__)


# This information is obtained upon registration of a new linkedin OAuth
# application here: https://linkedin.com/settings/applications/new
CLIENT_ID = '86q4vvodw7t8yt'
CLIENT_SECRET = '5AkKb4sSn12YsyB1'
REDIRECT_URI='http://127.0.0.1:5000/callback'
PROFILE_PAGE = 'https://www.linkedin.com/in/jonghyuk-lee/'
#authorization_base_url = 'https://www.linkedin.com/uas/oauth2/authorization'
#TOKEN_URL = 'https://www.linkedin.com/uas/oauth2/accessToken'
authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'


@app.route("/")
def request_authorization_code():
    print(f"\n{'='*60}\n{inspect.stack()[0][3]}\n")
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. linkedin)
    using an URL with a few key OAuth parameters.
    """
    linkedin = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    #print(f"\n linkedin.__dict__ :\n")
    #pp.pprint(linkedin.__dict__)
    authorization_url, state = linkedin.authorization_url(authorization_base_url)
    #print(f"\n authorization_url :\n{authorization_url}")

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    #print(f"\n session :\n{session}")
    return redirect(authorization_url)

@app.route("/callback", methods=["GET"])
def exchange_authorization_code_for_access_token():
    print(f"\n{'='*60}\n{inspect.stack()[0][3]}\n")
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    #print(f"\n request.__dict__ :")
    #pp.pprint(request.__dict__)

    linkedin = OAuth2Session(CLIENT_ID, state=session['oauth_state'], redirect_uri=REDIRECT_URI)
    #print(f"\n linkedin.__dict__ :\n")
    #pp.pprint(linkedin.__dict__)
    token = linkedin.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url, include_client_id=True)
    #print(f"\n token :\n{token}")

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.jobs'))

@app.route("/profile", methods=["GET"])
def profile():
    print(f"\n{'='*60}\n{inspect.stack()[0][3]}\n")
    """Fetching a protected resource using an OAuth 2 token.
    """
    linkedin = OAuth2Session(CLIENT_ID, token=session['oauth_token'], redirect_uri=REDIRECT_URI)
    #print(f"\n linkedin.__dict__ :\n")
    #pp.pprint(linkedin.__dict__)
    r = linkedin.get(PROFILE_PAGE)
    print(f"\n r. : {r}\n")
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(f"\n soup :\n{soup.prettify()}")
    #pp.pprint(r.__dict__)
    #return jsonify().json()
    #return redirect(PROFILE_PAGE)
    return json.dumps(r.text)

@app.route("/jobs", methods=["GET"])
def jobs():
    print(f"\n{'='*60}\n{inspect.stack()[0][3]}\n")
    linkedin = OAuth2Session(CLIENT_ID, token=session['oauth_token'], redirect_uri=REDIRECT_URI)
    keyword = 'Data%20Science'
    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location=Spain&locationId=es%3A0"
    r = linkedin.get(url)
    text = json.dumps(r.text, indent=4, sort_keys=True, ensure_ascii=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    if soup.find('ul', class_="jobs-search-content__results") is None:
        print(f"\n soup.find('div', class_='jobs-search-content__results-scrollable') is None.\n")
        return redirect(url_for('.jobs'))
    else:
        with open(file=f"/Users/sambong/pjts/career/career/htmls/{keyword}.html", mode='w') as f:
            f.write(soup.prettify(formatter='html5'))
            f.close()
        return text


@app.route("/view", methods=["GET"])
def view():
    print(f"\n{'='*60}\n{inspect.stack()[0][3]}\n")
    linkedin = OAuth2Session(CLIENT_ID, token=session['oauth_token'], redirect_uri=REDIRECT_URI)
    r = linkedin.get('https://www.linkedin.com/jobs/view/senior-data-science-at-hays-1201861215/?position=12&pageNum=0&originalSubdomain=es')

    soup = BeautifulSoup(r.text, 'html.parser')
    with open(file=f"/Users/sambong/pjts/career/career/htmls/senior-data-science-at-hays-1201861215.html", mode='w') as f:
        f.write(soup.prettify(formatter='html5'))
        f.close()
    if soup.find(string=re.compile('How you match')) is None:
        print(f"\n soup.find(string=re.compile('How you match')) is None.\n")
        return redirect(url_for('.view'))
    else:

        return json.dumps(r.text, indent=4, sort_keys=True, ensure_ascii=False)


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)
