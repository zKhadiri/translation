from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import requests,os,re,pytube,json,mimetypes,random,string
from django.views.decorators.csrf import csrf_exempt

def watch(request):
    if 'video' in request.COOKIES and 'srt' in request.COOKIES:
        return render(request,'translation/watch.html',{"video":request.COOKIES['video'],"srt":request.COOKIES['srt']})
    else:
        return render(request,'translation/error.html')

def index(request):
    response =  render(request,'translation/index.html', {'nbar': 'home'})
    response.delete_cookie('video')
    response.delete_cookie('srt')
    return response

def error_404(request, exception):
    return render(request,'translation/404.html', status = 404)

def creation_script(request):
    if 'video' in request.COOKIES:
        return render(request,'translation/creation_scripte.html',{"video":request.COOKIES['video']})
    else:
        return render(request,'translation/error.html')
    

@csrf_exempt
def generer_script(request):
    if 'video' in request.COOKIES:
        if request.method =="POST":
            sub_file = request.FILES['mySub']
            if str(sub_file).split('.')[-1].lower()=="srt":
                srt_name=''.join(random.choice(string.ascii_lowercase) for i in range(5))+".vtt"
                with open('{}/{}'.format(os.path.abspath('translation/media'),srt_name),"w")as f:
                    f.write("WEBVTT\n"+str(sub_file.read().decode()).replace(',','.'))
            else:
                srt_name=''.join(random.choice(string.ascii_lowercase) for i in range(5))+".vtt"
                fs = FileSystemStorage()
                fs.save(srt_name,sub_file)
            reponse= HttpResponse(json.dumps({'message': 'ok',}),content_type="application/json")
            reponse.set_cookie("srt",srt_name)
            return reponse
        return render(request,'translation/generer_script.html',{"video":request.COOKIES['video']})
    else:
        return render(request,'translation/error.html')
         
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
                    video_extension=''.join(random.choice(string.ascii_lowercase) for i in range(5))+'.'+url.split('/')[-1].split('.')[-1]
                    r = requests.get(url,stream=True)
                    with open('{}/{}'.format(os.path.abspath('translation/media'),video_extension), 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    reponse = HttpResponse(json.dumps({'message': 'ok'}),content_type="application/json")
                    reponse.set_cookie("video",video_extension)
                    return reponse
            except Exception:
                return HttpResponse(json.dumps({'message': 'not valid'}),content_type="application/json")
        
        elif url =='' and not "myVideo" in request.FILES:
            return HttpResponse(json.dumps({'message': 'empty'}),content_type="application/json")
        elif request.FILES['myVideo'] !="" and request.POST.get('link') !="":
            return HttpResponse(json.dumps({'message': 'url and files'}),content_type="application/json")
         
    reponse =  render(request,'translation/blog-single.html')
    reponse.delete_cookie('video')
    reponse.delete_cookie('srt')
    return reponse