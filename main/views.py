from django.shortcuts import render,redirect
from .models import CandidForm,candidate
from django.contrib.auth import logout as authout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages
from .choices import EVENT_OPTIONS,CERTIFICATE_OPTIONS,CERTIFICATE_PATHS
from django.db.models import Q
from .resources import *
from tablib import Dataset
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import os
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.validators import RegexValidator, EmailValidator
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, DictionaryObject, FloatObject, createStringObject
from io import BytesIO

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
            event=request.POST['event1']
            certi_type=request.POST['Certificate1']
            candid=candidate(name=name,email=email,college=college,certificate_type=certi_type,event=event)
            candid.save()
        except:
            messages.info('Email already exists')
    context={'events':EVENT_OPTIONS,'types':CERTIFICATE_OPTIONS}
    return render(request,'main/candidateform.html',context);

def update_candidate(request,pk):
    candid = candidate.objects.filter(id=pk).first()
    if request.method == 'POST':
        try:
            
            
            print(candid)
            candid.name = request.POST['name']
            candid.college = request.POST['college']
            candid.event = request.POST['event1']
            candid.certificate_type = request.POST['Certificate1']
            candid.email = request.POST['email']
            candid.save()
            return redirect('dashboard')
        except:
            messages.error(request, 'An error occurred while updating the candidate.')
    

    context = {
        'candidate':candid,
        
        'events': EVENT_OPTIONS,  # Make sure to define EVENT_OPTIONS in your context
        'types': CERTIFICATE_OPTIONS  # Make sure to define CERTIFICATE_OPTIONS in your context
    }
    return render(request, 'main/candidateform.html', context)



def delete_candidate(request, email):
    candid = candidate.objects.filter(email=email).first()
    candid.delete()
    return redirect('dashboard')

#add csv file
def addcsv(request):
    if request.method=="POST":
        candidate_resource = CandidateResource()
        dataset = Dataset()
        new_candidate = request.FILES.get('document')
        if new_candidate is None:
            messages.info(request, 'No file selected')
            return render(request, 'main/csvform.html')
        imported_data = dataset.load(new_candidate.read(),format = 'xlsx')
        for data in imported_data:
            
            value = candidate(
                data[0],
                data[1],
                data[2],
                data[3],
                False,
                False,
                data[4],
                data[5],
            )
            value.save()
        messages.info(request, 'data has been added successfully')
    return render(request,'main/csvform.html')

#logout view
def logout(request):
    authout(request)
    return redirect('login')


def add_text_to_pdf(input_path,name,college,event):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(2000,2000))
    if(input_path[0][0] == 'W' or input_path[0][0] == 'P' or input_path[0][0] == 'R' or input_path[0][0] == 'R1' or input_path[0][0] == 'R2'):
        can.setFontSize(22)
        can.drawString(430, 278, str(name))
        can.setFontSize(16)
        can.drawString(320, 248, str(college))
        can.setFontSize(22) 
        can.drawString(380, 217, str(event))
    else:
        can.setFontSize(22)
        can.drawString(427, 300, str(name))
        can.setFontSize(16)
        can.drawString(320, 270, str(college))
    can.save()
    
    packet.seek(0)
    new_pdf = PyPDF2.PdfReader(packet)

    # read your existing PDF
    with open(input_path[0][1], 'rb') as pdf_file:

        existing_pdf = PyPDF2.PdfReader(pdf_file)
        page = existing_pdf.pages[0]
        output = PyPDF2.PdfWriter()

        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

         # Create a byte stream to store the modified PDF content
        output_stream = BytesIO()
        output.write(output_stream)
        output_stream.seek(0)

        # Return the modified PDF content as a byte array
        return output_stream.getvalue()

# @login_required
def send_email(request,email):
    try:
        candid = candidate.objects.get(email=email)
    except candidate.DoesNotExist:
        candid = None

    if not candid or not candid.is_valid:
        return render(request, 'main/candidateform.html')

    context = {'candid': candid}

    # Map certificate types to email templates.
    # email_templates = {
    #     'Parliamentry Debate': 'main/emails/mailPD.html',
    #     'CA_G': 'main/emails/mailca.html',
    #     'CA_P': 'main/emails/mailca.html',
    #     'CA_S': 'main/emails/mailca.html',
    #     'CA_Part': 'main/emails/mailca.html',
    #     'P': 'main/emails/mailparticipant.html',
    #     'W': 'main/emails/mailwinner.html',
    #     'R1': 'main/emails/mailwinner.html',
    #     'R2': 'main/emails/mailwinner.html',
    #     'R': 'main/emails/mailwinner.html',
    #     'SA': 'main/emails/mailsa.html',
    #     'MW': 'main/emails/mailmswinner.html',
    #     'MP': 'main/emails/mailmsparticipant.html',
    # }

    # content = render_to_string(email_templates.get(candid.event, email_templates.get(candid.certificate_type)), context)

    name = candid.name
    competition = candid.event
    college = candid.college
    certi_type = candid.certificate_type
    # input_path = './certificates/Winner.pdf'
    input_path = list(filter(lambda x: x[0] == certi_type, CERTIFICATE_PATHS))
    # print(input_path)
    certificate_pdf = add_text_to_pdf(input_path,name,college,competition)

    email = EmailMessage(
        'Certificate of Achievement',
        f'Dear {candid.name},\n\nPlease find the attached certificate for your achievement in {candid.event}.\n\nCongratulations!',
        'your@gmail.com',  # Replace with your email
        [candid.email],
    )

    email.attach(f'{candid.name + candid.email}_certificate.pdf', certificate_pdf, 'application/pdf')

    email.send()

    candid.is_sent = True
    candid.save()

    return render(request, 'main/mail_sent.html', context, {'email': candid.email})
    