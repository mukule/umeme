from django.shortcuts import render

def custom_404(request, exception):
    return render(request, 'error_handling/404.html', status=404)

def custom_500(request):
    return render(request, 'error_handling/500.html', status=500)