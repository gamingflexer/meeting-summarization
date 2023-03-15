import requests
from django.shortcuts import redirect
from msal import PublicClientApplication
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status

def microsoft_login(request):
    # Define the Microsoft client ID and redirect URI
    client_id = ''
    client_credential = ""
    redirect_uri = 'http://localhost:8000/api/microsoft_callback'
    # Create a new instance of the PublicClientApplication class
    pca = PublicClientApplication(client_id=client_id,authority='https://login.microsoftonline.com/common')

    # Define the Microsoft scopes that you want to request
    scopes = ['User.Read']

    # Generate a Microsoft authorization URL and redirect the user to it
    auth_url = pca.get_authorization_request_url(scopes=scopes, redirect_uri=redirect_uri)

    return redirect(auth_url)


def microsoft_callback(request):
    # Define the Microsoft client ID and redirect URI
    client_id = ''
    redirect_uri = 'http://localhost:8000/api/microsoft_callback'
    client_credential = ""
    # Create a new instance of the PublicClientApplication class
    pca = PublicClientApplication(client_id=client_id, authority='https://login.microsoftonline.com/common')

    code = request.GET.get('code')
    print("code : ",code)
    # Use the authorization code to obtain an access token
    result = pca.acquire_token_by_authorization_code(code, scopes=['User.Read.All'], redirect_uri=redirect_uri)
    print(result)
    # Use the access token to make a request to the Microsoft Graph API
    access_token = result['access_token']
    graph_url = 'https://graph.microsoft.com/v1.0/me'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(graph_url, headers=headers)

    # Render the user's profile information on the page
    profile = response.json()
    print('success')
    return render(request, 'microsoft_profile.html', {'profile': profile})
