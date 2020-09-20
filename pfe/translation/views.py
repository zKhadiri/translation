from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import requests,os,re,pytube,json,mimetypes,random,string,subprocess,glob
from django.views.decorators.csrf import csrf_exempt
from requests.adapters import HTTPAdapter
from django.core.mail import send_mail

MEDIA_PATH=os.path.abspath('translation/media')

def convert(srt,video,random_name):
    subprocess.check_output(['ffmpeg','-i',srt,srt.split('.')[0]+'.ass'], cwd=MEDIA_PATH)
    subprocess.check_output(['ffmpeg','-threads','auto','-y', '-i',video, '-vf','ass='+srt.split('.')[0]+'.ass','-preset','ultrafast',random_name+'.mp4'],cwd=MEDIA_PATH)
    for file_name in glob.glob(MEDIA_PATH+'/'+srt.split('.')[0]+'.*'):
        os.remove(file_name)

def watch(request):
    if 'video' in request.COOKIES:
        return render(request,'translation/watch.html',{"video":request.COOKIES['video']})
    else:
        return render(request,'translation/error.html')

@csrf_exempt
def index(request):
    if request.method =="POST":
        user_name = request.POST['user_name']
        user_email = request.POST['user_email']
        user_description = request.POST['des']
        send_mail(
            "Email from "+user_name,
            user_description,
            user_email,
            ['test-tosend@mail.com'],
        )  
        return render(request,'translation/index.html', {"user_name":user_name})
    response =  render(request,'translation/index.html', {'nbar': 'home'})
    response.delete_cookie('video')
    return response

def error_404(request, exception):
    return render(request,'translation/404.html', status = 404)

@csrf_exempt
def creation_script(request):
    if 'video' in request.COOKIES and request.method == "GET":
        return render(request,'translation/creation_scripte.html',{"video":request.COOKIES['video']})
    
    elif 'video' in request.COOKIES and request.method == "POST":
        if request.POST.get('srt') != '':
            random_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
            srt_name=request.COOKIES['video'].split('.')[0]+'.vtt'
            with open('{}/{}'.format(MEDIA_PATH,srt_name),"w")as f:
                f.write("WEBVTT\n\r"+request.POST.get('srt').replace('\r\n','\n'))
            reponse= HttpResponse(json.dumps({'message': 'ok',}),content_type="application/json")
            convert(srt_name,request.COOKIES['video'],random_name)
            reponse.set_cookie("video",random_name+'.mp4')
            return reponse
        else:
            return HttpResponse(json.dumps({'message': 'not valid'}),content_type="application/json")
    
    else:
        return render(request,'translation/error.html')
    

@csrf_exempt
def generer_script(request):
    if 'video' in request.COOKIES:
        random_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        srt_name = request.COOKIES['video'].split('.')[0]+'.vtt'
        if request.method =="POST":
            sub_file = request.FILES['mySub']
            if str(sub_file).split('.')[-1].lower()=="srt":
                with open('{}/{}'.format(MEDIA_PATH,srt_name),"w")as f:
                    f.write("WEBVTT\n"+str(sub_file.read().decode()).replace(',','.'))
            else:
                fs = FileSystemStorage()
                fs.save(srt_name,sub_file)
            convert(srt_name,request.COOKIES['video'],random_name)
            reponse= HttpResponse(json.dumps({'message': 'ok',}),content_type="application/json")
            reponse.set_cookie("video",random_name+'.mp4')
            return reponse
            
        return render(request,'translation/generer_script.html',{"video":request.COOKIES['video']})
    else:
        return render(request,'translation/error.html')
         
@csrf_exempt
def play_video(request):
    if request.method == 'POST':
        url = request.POST.get('link')
        if "myVideo" in request.FILES and url =="":
            video_upload=''.join(random.choice(string.ascii_lowercase) for i in range(5))+'.'+str(request.FILES['myVideo']).split('.')[-1]
            video = request.FILES['myVideo']
            fs = FileSystemStorage()
            fs.save(video_upload,video)
            reponse= HttpResponse(json.dumps({'message': 'ok',}),content_type="application/json")
            reponse.set_cookie("video",video_upload)
            return reponse
        elif url != "" and url != None and not "myVideo" in request.FILES:
            try:
                if re.match(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$',url):
                    video = pytube.YouTube(url)
                    video_name=''.join(random.choice(string.ascii_lowercase) for i in range(5))
                    video.streams.get_highest_resolution().download(MEDIA_PATH,filename=video_name)
                    response = HttpResponse(json.dumps({'message': 'ok',}),content_type="application/json")
                    response.set_cookie('video',video_name+'.mp4')
                    return response
                elif mimetypes.MimeTypes().guess_type(url)[0].startswith("video"):
                    video_extension=''.join(random.choice(string.ascii_lowercase) for i in range(5))+'.'+url.split('/')[-1].split('.')[-1]
                    with requests.Session() as s:
                        s.mount('https://', HTTPAdapter(max_retries=20))
                        r = s.get(url,stream=True)
                        with open('{}/{}'.format(MEDIA_PATH,video_extension), 'wb') as f:
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
    return reponse