def session_user_id(request):
    return {'session_user_id': request.session.get('user_id')}

