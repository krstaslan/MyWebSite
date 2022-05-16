from urllib import request
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Room,Topic
from .forms import RoomForm
rooms=[
    {'id':1,'name':'Python 100 days cooding'},
    {'id':2, 'name':'Python sharing codes'},
    {'id':3, 'name':"Django learning"},
]
# #brings all elemet in queryset
# queryset=ModelName.onjects.all()
# #Retrieve a single object based on matced attribute
# queryItem= ModelName.objects.get(attribte='value')
# #Returns all items from table that match a particular attribute value
# queryset = ModelName.objects.filter(attribute='value')
# queryset = ModelName.objects.filter(attribute__startswith='value')
# queryset = ModelName.objects.filter(attribute__contains='value')
# queryset = ModelName.objects.filter(attribute__icontains='value')
# queryset = ModelName.objects.filter(attribute__gt='value')
# queryset = ModelName.objects.filter(attribute__gte='value')
# queryset = ModelName.objects.filter(attribute__lt='value')
# queryset = ModelName.objects.filter(attribute__lte='value')
# #Exclude any object matching a particular filter
# queryset = ModelName.objects.exclude(attribute='value')

def loginPage(request):
    page ='login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        try:
            user= User.objects.get(username=username)
        except:
            messages.error(request,'User doesn`t exist ')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)  
            return redirect('home')
        else:
            messages.error(request, 'Username or Password is not correct')
    context={'page':page}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page='register'
    return render(request, 'base/login_register.html')

def home(request):
    #in aline if statement. will chech if it first time to open page
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    #icontains to get all topic in specific search also it was py it brings python  
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(participants__icontains=q)        
        )
    topics=Topic.objects.all()
    room_count =rooms.count()
    context={'rooms':rooms, 'topics':topics ,'room_count':room_count}
    return render(request, 'base/home.html',context)

def room(request,pk):
    room =Room.objects.get(id=pk)
    context={'room':room}        
    return render(request, 'base/room.html',context)

#login requre to create new room if it logout it will redirect login page
@login_required(login_url='login')
def createRoom(request):
    form=RoomForm()
    if request.method=='POST': 
        form=RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context={'form':form}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    #it will fill with current values.thanks to "instance=room" sayesi
    form=RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('You are not allowed to update')

    if request.method=='POST':
        #it will update selected room.thanks to "instance=room" 
        form=RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form':form}
    return  render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed to update')
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':room})