import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


# AUTH0_DOMAIN = 'udacity-fsnd.auth0.com'
# ALGORITHMS = ['RS256']
# API_AUDIENCE = 'dev'

AUTH0_DOMAIN = 'somanath-kc.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'CoffeeShopApp'



## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO:[COMPLETED] implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        raise AuthError({
            'error': 401,
            'message': 'Missing authorization header.'
        }, 401)

    parts = auth_header.split(' ')
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'error': 401,
            'message': 'Authorization must contain bearer.'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'error': 401,
            'message': 'Invalid authorization header.'
        }, 401)

    token = parts[1]
    return token


'''
@TODO:[COMPLETED] implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if not payload.get('permissions'):
        raise AuthError({
            'error': 401,
            'message': 'No Permissions Found.'
        }, 401)

    if permission not in payload.get('permissions'):
        raise AuthError({
            'error': 401,
            'message': 'Not permitted.'
        }, 401)

'''
@TODO:[COMPLETED] implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    json_url = urlopen('https://{}/.well-known/jwks.json'.format(AUTH0_DOMAIN))
    jwks = json.loads(json_url.read())

    try:
        unverified_header = jwt.get_unverified_header(token)
    except:
        raise AuthError({
            'error': 401,
            'message': 'Invalid Token'
        }, 401)

    rsa_key = {}
    
    if 'kid' not in unverified_header:
        raise AuthError({
            'error': 401,
            'message': 'Invalid authorization header.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://{}/'.format(AUTH0_DOMAIN)
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
            'error': 401,
            'message': 'Token Expired'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
            'error': 401,
            'message': 'Invalid Claims.'
            }, 401)

        except Exception:
            raise AuthError({
            'error': 401,
            'message': 'Invalid headers.'
        }, 401)
    else:
        raise AuthError({
            'error': 401,
            'message': 'Invalid headers unable to find appropriate keys.'
        }, 401)

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator