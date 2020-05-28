from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request,'translation/index.html')


def error_404(request, exception):
    return render(request,'translation/404.html', status = 404)

def play_video(request):
    return render(request,'translation/blog-single.html')
