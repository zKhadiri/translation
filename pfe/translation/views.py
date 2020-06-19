from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import requests,os,re,pytube,sys,json,mimetypes,random,string
from django.views.decorators.csrf import csrf_exempt


def index(request):
    response =  render(request,'translation/index.html', {'nbar': 'home'})
    response.delete_cookie('video')
    return response
def error_404(request, exception):
    return render(request,'translation/404.html', status = 404)

def creation_script(request):
    
    return render(request,'translation/creation_scripte.html',{"video":request.COOKIES['video']})

def generer_script(request):
    print(request.COOKIES)
    return render(request,'translation/generer_script.html',{"video":request.COOKIES['video']})

@csrf_exempt
def play_video(request):
    if request.method == 'POST':
        url = request.POST.get('link')
        if "myVideo" in request.FILES and url =="":
            video = request.FILES['myVideo']
            fs = FileSystemStorage()
            fs.save(video.name,video)
            reponse= HttpResponse(json.dumps({'message': 'ok',}),content_type="application/json")
            reponse.set_cookie("video",video.name)
            return reponse
        elif url != "" and url != None and not "myVideo" in request.FILES:
            try:
                if re.match(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$',url):
                    video = pytube.YouTube(url)
                    video_name=''.join(random.choice(string.ascii_lowercase) for i in range(5))
                    video.streams.get_highest_resolution().download(os.path.abspath('translation/media'),filename=video_name)
                    response = HttpResponse(json.dumps({'message': 'ok',}),content_type="application/json")
                    response.set_cookie('video',video_name+'.mp4')
                    return response
                elif mimetypes.MimeTypes().guess_type(url)[0].startswith("video"):
                    local_filename = url.split('/')[-1]
                    r = requests.get(url,stream=True)
                    with open('{}/{}'.format(os.path.abspath('translation/media'),local_filename), 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    reponse = HttpResponse(json.dumps({'message': 'ok'}),content_type="application/json")
                    reponse.set_cookie("video",local_filename)
                    return reponse
            except Exception:
                return HttpResponse(json.dumps({'message': 'not valid'}),content_type="application/json")
        
        elif url =='' and not "myVideo" in request.FILES:
            return HttpResponse(json.dumps({'message': 'empty'}),content_type="application/json")
        elif request.FILES['myVideo'] !="" and request.POST.get('link') !="":
            return HttpResponse(json.dumps({'message': 'url and files'}),content_type="application/json")
         
    reponse =  render(request,'translation/blog-single.html')
    reponse.delete_cookie('video')
    return reponse