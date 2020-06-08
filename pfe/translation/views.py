from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import requests,os,re,pytube,sys
from clint.textui import progress
from time import sleep




def index(request):
    return render(request,'translation/index.html', {'nbar': 'home'})


def error_404(request, exception):
    return render(request,'translation/404.html', status = 404)

def play_video(request):
    global file_size
    if request.method == 'POST' and 'Select' in request.POST:
        print (request)
        video = request.FILES['myVideo']
        fs = FileSystemStorage()
        fs.save(video.name,video)
    elif request.method=='POST' and 'Search' in request.POST:
        url = request.POST.get('link')
        if re.match(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$',url):
            video = pytube.YouTube(url, on_progress_callback=progress_function)
            video_type = video.streams.filter(progressive = True, file_extension = "mp4").first()
            file_size = video_type.filesize
            video.streams.get_highest_resolution().download(os.path.abspath('translation/media'))
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

def progress_function(stream, chunk, file_handle, bytes_remaining):
    print(round((1-bytes_remaining/file_size.filesize)*100, 3), '% done...')
    