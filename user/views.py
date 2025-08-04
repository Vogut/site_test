import string
import random
import time
from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.cache import cache

from .models import Profile
from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
# Create your views here.
def login(request):
    if request.method == 'POST':#提交数据
        login_form = LoginForm(request.POST)
        
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from',reverse('home')))
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request,'user/login.html',context)

def login_for_modal(request):
    data={}
    login_form = LoginForm(request.POST)
    
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def register(request):
    
    if request.method == 'POST':#提交数据
        reg_form = RegForm(request.POST)
        
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            user = User.objects.create_user(username=username,email=email,password=password)
            user.save()
            cache.delete(f'{email}')
            user = auth.authenticate(request, username=username, password=password)
            auth.login(request,user)
            return redirect(request.GET.get('from',reverse('home')))
    else:
        reg_form = RegForm()
    context = {}
    context['reg_form'] = reg_form
    return render(request,'user/register.html',context)

def logout(request):
    auth.logout(request)

    return redirect(request.GET.get('from',reverse('home')))

def user_info(request):
    context ={}

    return render(request,'user/user_info.html',context)

def change_nickname(request):
    redirect_to = request.GET.get('from',reverse('home'))
    if request.method == 'POST':#提交数据
        change_nickname_form = ChangeNicknameForm(request.POST, user = request.user)
        
        if change_nickname_form.is_valid():
            nickname_new = change_nickname_form.cleaned_data['nickname_new']
            profile, _ = Profile.objects.get_or_create(user = request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        change_nickname_form = ChangeNicknameForm()
    context = {}
    context['form'] = change_nickname_form
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['return_url'] = redirect_to
    return render(request,'form.html',context)

def bind_email(request):
    redirect_to = request.GET.get('from',reverse('home'))
    if request.method == 'POST':#提交数据
        bind_email_form = BindEmailForm(request.POST, request = request)
        
        if bind_email_form.is_valid():
            email = bind_email_form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            cache.delete(f'{email}')
            return redirect(redirect_to)
    else:
       bind_email_form = BindEmailForm()
    context = {}
    context['form'] = bind_email_form
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '提交'
    context['return_url'] = redirect_to
    return render(request,'user/bind_email.html',context)

def send_verification_code(request):
    email = request.POST.get('email','')
    data={}
    if email != '':
        verification_code = ''.join(random.sample(string.digits+string.ascii_letters, 4))
        cache.set(f"{email}", verification_code, 300)
        request.session['bind_email_code'] = verification_code 
        send_mail(
            "绑定邮箱",
            f"验证码 {verification_code}",
            "398256221@qq.com",
            [email],
            fail_silently=False,
        )
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)

def forgot_password(request):
    redirect_to = reverse('login')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除cache
            cache.delete(f'{email}')
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '重置'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/forgot_password.html', context)