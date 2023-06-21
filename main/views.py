from django.shortcuts import render,redirect
from .models import CandidForm,candidate
from django.contrib.auth import logout as authout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages
from .choices import EVENT_OPTIONS,CERTIFICATE_OPTIONS
from django.db.models import Q
# Create your views here.
# Login view
def login(request):
    if request.method=='POST':
        username=request.POST['email']
        password=request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            redirect('dashboard')
        else:
            messages.info(request, "Invalid Crendentials")
            return render(request,'main/login.html')
    return render(request,'main/login.html')

# Dashboard View
def dashboard(request,sent=0):
    if sent==1:
        context={'candidates' :candidate.objects.filter(is_sent=True)}
    else:
        context={'candidates' :candidate.objects.filter(Q(is_sent=False) | Q(is_valid=False))}
    
    return  render(request,'main/dashboard.html',context)

#add Candiate form
def addCandidate(request):
    if request.method=='POST':
        try:
            name=request.POST['name']
            email=request.POST['email']
            college=request.POST['college']
            event=request.POST['event']
            certi_type=request.POST['Certificate']
            candid=candidate(name=name,email=email,college=college,certificate_type=certi_type,event=event)
            candid.save()
        except:
            messages.info('Email already exists')
    context={'events':EVENT_OPTIONS,'types':CERTIFICATE_OPTIONS}
    return render(request,'main/candidateform.html',context);

def delete_candidate(request, email):
    candid = candidate.objects.filter(email=email).first()
    candid.delete()
    return redirect('dashboard')
#logout view
def logout(request):
    authout(request)
    return redirect('login')