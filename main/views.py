from django.shortcuts import render,redirect
from .models import CandidForm,candidate
from django.contrib.auth import logout as authout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages
from .choices import EVENT_OPTIONS,CERTIFICATE_OPTIONS
from django.db.models import Q
from .resources import *
from tablib import Dataset
from django.http import HttpResponse
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
import pdfkit
import tempfile
import os
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.validators import RegexValidator, EmailValidator
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

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


def select_certificate_template(candid):
    if candid.event == 'Parliamentry Debate':
        return 'certificate/certificatePD.html'
    elif candid.certificate_type == 'SA':
        return 'certificate/certificateSA.html'
    elif candid.certificate_type == 'P': 
        return 'certificate/certificateParticipation.html'
    elif candid.certificate_type == 'CA_P': 
        return 'certificate/certificateCAPlat.html'
    elif candid.certificate_type == 'CA_G': 
        return 'certificate/certificateCAGold.html'
    elif candid.certificate_type == 'CA_S': 
        return 'certificate/certificateCASilver.html'
    elif candid.certificate_type == 'CA_Part': 
        return 'certificate/certificateCAPart.html'
    elif candid.certificate_type == 'W': 
        return 'certificate/certificateWinner.html'
    elif candid.certificate_type == 'R1': 
        return 'certificate/certificateFirstRunner.html'
    elif candid.certificate_type == 'R2': 
        return 'certificate/certificateSecondRunner.html'
    elif candid.certificate_type == 'R':
        return 'certificate/certificaterunner.html'
    elif candid.certificate_type == 'MP':
        return 'certificate/certificateManshaktiParticipant.html'
    elif candid.certificate_type == 'MW':
        return 'certificate/certificateManshaktiWinner.html'
    # ... Add other conditions for different certificate types

    return 'certificate/default_certificate.html'  # Default template if no condition is met

def create_certificate_pdf(candid):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{candid.name + candid.email}_certificate.pdf"'

    # Select the appropriate certificate template based on the certificate type.
    template_path = select_certificate_template(candid)

    # Render the HTML content.
    html_content = render_to_string(template_path, {
        'candid_name': candid.name,
        'candid_event': candid.event,
        # 'candid_position': candid.position,
        'candid_college': candid.college,
        # 'candid_achievement': candid.special_achievement,
    })

    # Convert the HTML content to a PDF file.
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        pdf_path = temp_file.name + '.pdf'

    pdfkit.from_string(html_content, pdf_path, configuration=pdfkit.configuration(wkhtmltopdf='main\wkhtmltopdf.exe'))

    # Read the PDF file content.
    with open(pdf_path, 'rb') as pdf_file:
        pdf_content = pdf_file.read()

    # Remove the temporary PDF file.
    os.remove(pdf_path)

    # Write the PDF content to the response object.
    response.write(pdf_content)

    return response


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

    certificate_pdf = create_certificate_pdf(candid)

    email = EmailMessage(
        'Certificate of Achievement',
        f'Dear {candid.name},\n\nPlease find the attached certificate for your achievement in {candid.event}.\n\nCongratulations!',
        'your@gmail.com',  # Replace with your email
        [candid.email],
    )

    email.attach(f'{candid.name + candid.email}_certificate.pdf', certificate_pdf.getvalue(), 'application/pdf')

    email.send()

    candid.is_sent = True
    candid.save()

    return render(request, 'main/mail_sent.html', context, {'email': candid.email})
    