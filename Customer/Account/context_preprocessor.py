# login :- session

def is_logged_in(request):
    user_id = request.session.get('user_id')
    return {
        'is_logged_in': user_id
    }