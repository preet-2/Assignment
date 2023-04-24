from django.shortcuts import redirect

from rest_framework.decorators import api_view
from rest_framework.response import Response

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os
import datetime

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
#Gather secrets from this file
CLIENT_SECRETS_FILE = "credentials.json"

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile', 'openid'
]
REDIRECT_URL = 'https://google-calendar-integration.preetbhatia.repl.co/rest/v1/calendar/redirect/'


@api_view(['GET'])
def GoogleCalendarInitView(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = REDIRECT_URL

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    request.session['state'] = state

    # URL for login screen
    return Response({"authorization_url": authorization_url})


@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URL

    authorization_response = request.get_full_path()
    flow.fetch_token(authorization_response=authorization_response)


    credentials = flow.credentials
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # If credentials are not in session redirect to login
    if 'credentials' not in request.session:
        return redirect('v1/calendar/init')

    # otherwise load credentials from the session
    credentials = google.oauth2.credentials.Credentials(
        **request.session['credentials'])

    service = googleapiclient.discovery.build('calendar',
                                              'v3',
                                              credentials=credentials,
                                              static_discovery=False)

    currentTime = datetime.datetime.utcnow().isoformat() + 'Z'
    # Get upcoming 100 events
    print('Getting the upcoming 100 events')
    events_result = service.events().list(calendarId='primary',
                                          timeMin=currentTime,
                                          maxResults=100,
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return Response({"message": "No upcoming events found"})
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    return Response({"events": events})
