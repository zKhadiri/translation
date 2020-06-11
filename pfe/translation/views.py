from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import requests,os,re,pytube,sys,json
import pytube
from time import sleep
from django.views.decorators.csrf import csrf_exempt

video_format=['mp4','webm','ogv','3gp','mkv']

def index(request):
    return render(request,'translation/index.html', {'nbar': 'home'})

def error_404(request, exception):
    return render(request,'translation/404.html', status = 404)

def creation_script(request):
    return render(request,'translation/creation_scripte.html')

def generer_script(request):
    return render(request,'translation/generer_script.html')

@csrf_exempt
def play_video(request):
    if request.method == 'POST':
        url = request.POST.get('link')
        if "myVideo" in request.FILES:
            video = request.FILES['myVideo']
            fs = FileSystemStorage()
            fs.save(video.name,video)
            return HttpResponse(json.dumps({'message': 'ok',}),content_type="application/json")
        elif url != "" and url != None:
            if re.match(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$',url) and url != "":
                video = pytube.YouTube(url)
                video.streams.get_highest_resolution().download(os.path.abspath('translation/media'))
            elif [frm for frm in video_format if frm in url]:#''.join(video_format) in url:
                local_filename = url.split('/')[-1]
                r = requests.get(url,stream=True)
                with open('{}/{}'.format(os.path.abspath('translation/media'),local_filename), 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            return HttpResponse(json.dumps({'message': 'ok',}),content_type="application/json")
        elif url =='' and not "myVideo" in request.FILES:
            return HttpResponse(json.dumps({'message': 'empty',}),content_type="application/json")
            
    return render(request,'translation/blog-single.html')