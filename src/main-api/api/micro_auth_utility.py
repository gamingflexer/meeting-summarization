import random
import string

import msal
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
# User = get_user_model()


graph_url = "https://graph.microsoft.com/v1.0"
scopes = ['User.Read','https://graph.microsoft.com/OnlineMeetingTranscript.Read.All','https://graph.microsoft.com/Calendars.Read','https://graph.microsoft.com/Contacts.Read','https://graph.microsoft.com/Mail.ReadBasic']



# not using cache
def load_cache(request):
    cache = msal.SerializableTokenCache()
    if request.session.get("token_cache"):
        cache.deserialize(request.session["token_cache"])
    return cache


def save_cache(request, cache):
    if cache.has_state_changed:
        request.session["token_cache"] = cache.serialize()


def get_msal_app(cache=None):
    # Initialize the MSAL confidential client
    auth_app = msal.ConfidentialClientApplication(
        client_id ="",
        authority="",
        client_credential="",
        token_cache=cache,
    )
    return auth_app


def get_sign_in_flow():
    auth_app = get_msal_app()
    return auth_app.initiate_auth_code_flow(scopes = scopes, redirect_uri="http://localhost:8000/api/microsoft_callback")


def get_token_from_code(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)
    flow = request.session.pop("auth_flow", {})
    result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
    save_cache(request, cache)
    print('here1')
    return result


def get_token(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)

    accounts = auth_app.get_accounts()
    if accounts:
        result = auth_app.acquire_token_silent(scopes = scopes, account=accounts[0])
        save_cache(request, cache)
        return result["access_token"]




