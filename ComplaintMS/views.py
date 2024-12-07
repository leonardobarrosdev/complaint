from datetime import datetime

import ipdb
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count, Q
from django.urls import reverse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import Complaint
from .forms import (
    UserRegisterForm,
    ProfileUpdateForm,
    ProfileForm,
    ComplaintForm,
    ProfileUpdateForm,
    StatusUpdate
)

#loading page
def index(request):
    return render(request,"ComplaintMS/home.html")

def about_us(request):
    return render(request,"ComplaintMS/aboutus.html")

def login(request):
    return render(request,"ComplaintMS/login.html")

def logout_view(request):
    logout(request)
    return render(request, "ComplaintMS/logout.html")

def signin(request):
    return render(request,"ComplaintMS/signin.html")

#get the count of all the submitted complaints, solved, unsolved.
def counter(request):
    total = Complaint.objects.all().count()
    unsolved = Complaint.objects.all().exclude(status='1').count()
    solved = Complaint.objects.all().exclude(Q(status='3') | Q(status='2')).count()
    dataset = Complaint.objects.values('type_of_complaint').annotate(total=Count('status'),
        solved=Count('status', filter=Q(status='1')),
        notsolved=Count('status', filter=Q(status='3')),
        inprogress=Count('status',filter=Q(status='2'))).order_by('type_of_complaint')
    args = {'total': total, 'unsolved': unsolved, 'solved': solved, 'dataset': dataset}
    return render(request,"ComplaintMS/counter.html", args)

#changepassword for grievance member.
def change_password_g(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.add_message(request,messages.SUCCESS, f'Your password was successfully updated!')
            return redirect('change_password_g')
        else:
            messages.add_message(request,messages.WARNING, f'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'ComplaintMS/change_password_g.html', {'form': form})
    return render(request,"ComplaintMS/change_password_g.html")

#registration page.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            if profile.user_id is None:
                profile.user_id=user.id
            profile.save()
            messages.add_message(request,messages.SUCCESS, f' Registered Successfully ')
            return redirect('/login/')
    else:
        form = UserRegisterForm()
        profile_form = ProfileForm()
    context={'form': form, 'profile_form': profile_form }
    return render(request, 'ComplaintMS/register.html', context)

#login based on user.
def login_redirect(request):
    if request.user.profile.type_user=='student':
        return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponseRedirect('/counter/')

@login_required
def dashboard(request):
    if request.method == 'POST':
        p_form=ProfileUpdateForm(request.POST, instance=request.user)
        profile_update_form=ProfileUpdateForm(request.POST, instance=request.user.profile)
        if p_form.is_valid() and profile_update_form.is_valid():
                user=p_form.save()
                profile=profile_update_form.save(commit=False)
                profile.user=user
                profile.save()
                messages.add_message(request,messages.SUCCESS, f'Updated Successfully')
                return render(request,'ComplaintMS/dashboard.html',)
    else:
        p_form = ProfileUpdateForm(instance=request.user)
        profile_update_form = ProfileUpdateForm(instance=request.user.profile)
    context={'p_form':p_form, 'profile_update_form':profile_update_form}
    return render(request, 'ComplaintMS/dashboard.html',context)

#change password for user.
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.add_message(request,messages.SUCCESS, f'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.add_message(request,messages.WARNING, f'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'ComplaintMS/change_password.html', {'form': form})

#complaints handling and submission section.
@login_required
def complaints(request):
    if request.method == 'POST':
        form=ComplaintForm(request.POST)
        if form.is_valid():
           instance = form.save(commit=False)
           instance.user = request.user
           mail=request.user.email
           send_mail('Hi Complaint has been Received', 'Thank you for letting us know of your concern, Have a Cookie while we explore into this matter.  Dont Reply to this mail', 'testerpython13@gmail.com', [mail], fail_silently=False)
           instance.save()
           messages.add_message(request,messages.SUCCESS, f'Your complaint has been registered!')
           return render(request,'ComplaintMS/comptotal.html',)
    else:
        form = ComplaintForm(request.POST)
    context = {'complaint_form': form,}
    return render(request,'ComplaintMS/comptotal.html', context)

@login_required
def list(request):
    c=Complaint.objects.filter(user=request.user).exclude(status='1')
    result=Complaint.objects.filter(user=request.user).exclude(Q(status='3') | Q(status='2'))
    args={'c': c, 'result': result}
    return render(request,'ComplaintMS/Complaints.html',args)

@login_required
def solved_list(request):
    result = Complaint.objects.filter(user=request.user).exclude(Q(status='3') | Q(status='2'))
    args={'result': result}
    return render(request,'ComplaintMS/solvedcomplaint.html', args)

@login_required
def all_complaints(request):
        complaint = Complaint.objects.all().exclude(status='1')
        comp = request.GET.get("search")
        drop = request.GET.get("drop")
        if drop:
            complaint = complaint.filter(Q(type_of_complaint__icontains=drop))
        if comp:
            complaint = complaint.filter(Q(type_of_complaint__icontains=comp)|Q(description__icontains=comp)|Q(subject__icontains=comp))
        if request.method=='POST':
                cid = request.POST.get('cid2')
                uid = request.POST.get('uid')
                project = Complaint.objects.get(id=cid)
                forms = StatusUpdate(request.POST, instance=project)
                if forms.is_valid():
                    obj = forms.save(commit=False)
                    mails = User.objects.filter(id=uid)
                    for mail in mails:
                        m = mail.email
                        send_mail('Hi, Complaint has been Resolved ', 'Thanks for letting us know of your concern, Hope we have solved your issue. Dont Reply to this mail', 'testerpython13@gmail.com', [m],fail_silently=False)
                    obj.save()
                    messages.add_message(request,messages.SUCCESS, f'The complaint has been updated!')
                    return HttpResponseRedirect(reverse('all_complaints'))
                else:
                    return render(request,'ComplaintMS/AllComplaints.html')
                     #testing
        else:
            forms=StatusUpdate()
        #c=Complaint.objects.all().exclude(status='1')
        args={'c': complaint,'forms': forms, 'comp': comp}
        return render(request,'ComplaintMS/AllComplaints.html', args)

@login_required
def solved(request):
        cid=request.POST.get('cid2')
        c=Complaint.objects.all().exclude(Q(status='3') | Q(status='2'))
        comp=request.GET.get("search")
        drop=request.GET.get("drop")
        if drop:
            c=c.filter(Q(type_of_complaint__icontains=drop))
        if comp:
            c=c.filter(Q(type_of_complaint__icontains=comp)|Q(description__icontains=comp)|Q(subject__icontains=comp))
        if request.method=='POST':
            cid=request.POST.get('cid2')
            print(cid)
            project = Complaint.objects.get(id=cid)
            forms=StatusUpdate(request.POST,instance=project)
            if forms.is_valid():

                    obj=forms.save(commit=False)
                    obj.save()
                    messages.add_message(request,messages.SUCCESS, f'The complaint has been updated!')
                    return HttpResponseRedirect(reverse('solved'))
            else:
                    return render(request,'ComplaintMS/solved.html')
             #testing
        else:
            forms=StatusUpdate()
        #c=Complaint.objects.all().exclude(Q(status='3') | Q(status='2'))
        args={'c':c,'forms':forms,'comp':comp}
        return render(request,'ComplaintMS/solved.html',args)

#allcomplaints pdf viewer.
def pdf_viewer(request):
    detail_string={}
    #detailname={}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=Complaint_id.pdf'
    p = canvas.Canvas(response,pagesize=A4)
    
    cid=request.POST.get('cid')
    uid=request.POST.get('uid')
    #print(cid)
    
    details = Complaint.objects.filter(id=cid).values('description')
    name = Complaint.objects.filter(id=cid).values('user_id')
    '''Branch = Complaint.objects.filter(id=cid).values('Branch')'''
    subject = Complaint.objects.filter(id=cid).values('subject')
    Type = Complaint.objects.filter(id=cid).values('type_of_complaint')
    Issuedate = Complaint.objects.filter(id=cid).values('Time')
    #date_format1 = "%Y-%m-%d %H:%M:%S.%f%z"
   
    
    for val in details:
            detail_string=("{}".format(val['description']))
    for val in name:
           detailname=("User: {}".format(val['user_id']))
    '''for val in Branch:
            detailbranch=("Branch: {}".format(val['Branch']))'''
    for val in subject:
            detailsubject=("subject: {}".format(val['subject']))
    for val in Type:
            detailtype=("{}".format(val['type_of_complaint']))
            
    for val in Issuedate:
            ptime=("{}".format(val['Time']))
            detailtime=("Time of Issue/ Time of Solved: {}".format(val['Time']))
    #detail_string = u", ".join(("Desc={}".format(val['description'])) for val in details) 
    date_format = "%Y-%m-%d"
    a = datetime.strptime(str(datetime.now().date()), date_format)
    b = datetime.strptime(str(ptime), date_format)
    delta = a - b
    print(b)
    print(a)
    print (delta.days )       
    if detailtype=='1':
            detailtype="Type of Complaint: ClassRoom"
    if detailtype=='3':
            detailtype="Type of Complaint: Management"
    if detailtype=='2':
            detailtype="Type of Complaint: Teacher"
    if detailtype=='4':
            detailtype="Type of Complaint: School"
    if detailtype=='5':
            detailtype="Type of Complaint: Other"

    p.drawString(25, 770,"Report:")
    p.drawString(30, 750,detailname)
    ''' p.drawString(30, 730,detailbranch)'''
    p.drawString(30, 710,detailtype)
    p.drawString(30, 690,detailtime)
    p.drawString(30, 670,detailsubject)
    p.drawString(30, 650,"description:")
    p.drawString(30, 630,detail_string)

    p.showPage()
    p.save()
    return response

#complaints pdf view.
@login_required
def pdf_view(request):
    detail_string={}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=complaint_id.pdf'
    
    p = canvas.Canvas(response,pagesize=A4)
    cid=request.POST.get('cid')
    #print(cid)
    details = Complaint.objects.filter(id=cid).values('description')
    name = User.objects.filter(username=request.user.username).values('username')
    #Branch = Complaint.objects.filter(id=cid).values('Branch')
    subject = Complaint.objects.filter(id=cid).values('subject')
    Type = Complaint.objects.filter(id=cid).values('type_of_complaint')
    Issuedate = Complaint.objects.filter(id=cid).values('Time')

    for val in details:
            detail_string=("{}".format(val['description']))
    for val in name:
            detailname=("User: {}".format(val['username']))
    #for val in Branch:
            #detailbranch=("Branch: {}".format(val['Branch']))
    for val in subject:
            detailsubject=("subject: {}".format(val['subject']))
    for val in Type:
            detailtype=("{}".format(val['type_of_complaint']))
            
    for val in Issuedate:
            detailtime=("Time of Issue: {}".format(val['Time']))
    #detail_string = u", ".join(("Desc={}".format(val['description'])) for val in details) 

    if detailtype=='1':
            detailtype="Type of Complaint: ClassRoom"
    if detailtype=='3':
            detailtype="Type of Complaint: Management"
    if detailtype=='2':
            detailtype="Type of Complaint: Teacher"
    if detailtype=='4':
            detailtype="Type of Complaint: School"
    if detailtype=='5':
            detailtype="Type of Complaint: Other"

    p.drawString(25, 770,"Report:")
    p.drawString(30, 750,detailname)
    #p.drawString(30, 730,detailbranch)
    p.drawString(30, 710,detailtype)
    p.drawString(30, 690,detailtime)
    p.drawString(30, 670,detailsubject)
    p.drawString(30, 650,"description:")
    p.drawString(30, 630,detail_string)

    p.showPage()
    p.save()
    return response




             

