from functools import wraps

from flask import Response, current_app, request, session


def requires_auth(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        if session.get('bcss_authenticated'):
            return view(*args, **kwargs)

        auth = request.authorization
        expected_username = current_app.config.get('SITE_USER')
        expected_password = current_app.config.get('SITE_PASSWORD')
        if (
            not auth
            or not expected_username
            or not expected_password
            or auth.username != expected_username
            or auth.password != expected_password
        ):
            return Response(
                'Could not verify your access level for that URL.\n'
                'You have to login with proper credentials',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'},
            )

        session['bcss_authenticated'] = True
        session.permanent = True
        return view(*args, **kwargs)

    return decorated
