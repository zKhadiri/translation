from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import requests,os,re,pytube
from clint.textui import progress
from time import sleep

def index(request):
    return render(request,'translation/index.html', {'nbar': 'home'})


def error_404(request, exception):
    return render(request,'translation/404.html', status = 404)

def play_video(request):
    if request.method == 'POST' and 'Select' in request.POST:
        print (request)
        video = request.FILES['myVideo']
        fs = FileSystemStorage()
        fs.save(video.name,video)
    elif request.method=='POST' and 'Search' in request.POST:
        url = request.POST.get('link')
        if re.match(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$',url):
            video = pytube.YouTube(url)
            video.streams.all()
            for tag in video.streams:
                print(tag)
            video.streams.get_by_itag(22).download(os.path.abspath('translation/media')) 
        else:
            local_filename = url.split('/')[-1]
            r = requests.get(url,stream=True)
            total_length = int(r.headers.get('content-length'))
            with open('{}/{}'.format(os.path.abspath('translation/media'),local_filename), 'wb') as f:
                for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
                    if chunk: 
                        f.write(chunk)
                        f.flush()
            sleep(1)
    return render(request,'translation/blog-single.html')

