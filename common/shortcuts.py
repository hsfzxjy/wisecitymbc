from django.shortcuts import redirect

def redirect_back(request):
    url = request.META.get("HTTP_REFERER", "")
    return redirect(url)