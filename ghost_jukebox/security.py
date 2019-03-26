from flask_httpauth import HTTPBasicAuth
from ghost_jukebox import conf

# put straightforward httpbasic auth on each page, just cause I don't want undue traffic really
# might remove this eventually, who knows
basic_auth = HTTPBasicAuth()


# make it so that you have to be connected to my home network to do the important bits
def is_home(request):
    request_ip = request.environ['HTTP_X_FORWARDED_FOR']
    return request_ip == conf.host_ip

def home_auth(endpoint):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_home(request):
            return f(*args, **kwargs)
        else:
            abort(403)
    return decorated_function
        
