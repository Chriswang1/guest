from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event,Guest
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

# Create your views here.
def index(request):
    return render(request,"index.html")
#登录动作
def login_action(request):
    if request.method=='POST':
       username=request.POST.get('username','')
       password=request.POST.get('password','')
       user=auth.authenticate(username=username,password=password)
       if user is not None:
         auth.login(request,user)#登录动作
         request.session['user']=username
         response = HttpResponseRedirect('/event_manage/')
         return response
       else:
         return render(request,'index.html',{'error':'username or password error!'})
       #if username=='admin' and password=="admin123":
       # response = HttpResponseRedirect('/event_manage/')
       # #response.set_cookie('user',username,3600)#添加浏览器cookie
         request.session['user']=username#将session信息记录到浏览器
       #  return response
       #else:
       # return render(request,'index.html',{'error':'username or password error!'})

#登录成功
@login_required
def event_manage(request):
    event_list=Event.objects.all()
    #username=request.COOKIES.get('user','')#读取浏览器cookie
    username=request.session.get('user','')#读取浏览器session
    return render(request,"event_manage.html",{"user":username,"events":event_list})

#发布会名称搜索
@login_required
def search_name(request):
   username=request.session.get('user','')
   search_name=request.GET.get("name","")
   event_list=Event.objects.filter(name__contains=search_name)
   return render(request,"event_manage.html",{"user":username,"events":event_list})
#嘉宾管理
@login_required
def guest_manage(request):
     username=request.session.get('user','')
     guest_list=Guest.objects.all()
     paginator = Paginator(guest_list,2)
     page=request.GET.get('page')
     try:
        contacts=paginator.page(page)
     except PageNotAnInteger:
     #如果page不是一个整数，取第一页面的数据
        contacts=paginator.page(1)
     except EmptyPage:
     #如果page不在范围，取最后一个页面
        contacts=paginator.page(paginator.num_pages)
     return render(request,"guest_manage.html",{"user":username,"guests":contacts})


#签到页面
@login_required
def sign_index(request,eid):
    event =get_object_or_404(Event,id=eid)
    count=Guest.objects.count()
    count1=Guest.objects.filter(sign='1').count()
    return render(request,'sign_index.html',{'event':event,'count1':count1,'count':count})

#签到动作
@login_required
def sign_index_action(request,eid):
    event=get_object_or_404(Event,id=eid)
    phone=request.POST.get('phone','')
    print(phone)
    count=Guest.objects.count()
    count1=Guest.objects.filter(sign='1').count()
    result=Guest.objects.filter(phone=phone)
    if not result:
       return render(request,'sign_index.html',{'event':event,'hint':'手机号错误.','count1':count1,'count':count})
    result=Guest.objects.filter(phone=phone,event=eid)
    if not result:
       return render(request,'sign_index.html',{'event':event,'hint':'会议或者手机号错误.','count1':count1,'count':count})
    result=Guest.objects.get(phone=phone,event=eid)
    if result.sign:
       return render(request,'sign_index.html',{'event':event,'hint':'该用户已签到.','count1':count1,'count':count})
    else:
       Guest.objects.filter(phone=phone,event=eid).update(sign='1')
       return render(request,'sign_index.html',{'event':event,'hint':'签到成功','guest':result,'count1':count1,'count':count})

#退出登录界面
@login_required
def logout(request):
    auth.logout(request)
    response=HttpResponseRedirect('#')
    return response
