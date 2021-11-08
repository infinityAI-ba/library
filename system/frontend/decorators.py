from django.shortcuts import redirect


def allowerd_users(allowerd_rules = []):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            for roule in allowerd_rules:
                if request.user.groups.filter(name = roule):
                    return view_func(request, *args, **kwargs)    
            return redirect('error-view')

        return wrapper_func
    return decorator