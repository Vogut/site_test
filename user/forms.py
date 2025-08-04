from typing import Any
from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.cache import cache
from httpx import request
class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', widget=forms.TextInput(
                                attrs={'class':'form-control','placeholder':'请输入用户名'}))
    password = forms.CharField(label='密码', widget=forms.PasswordInput(
                                attrs={'class':'form-control','placeholder':'请输入密码'}))

    def clean(self) -> dict[str, Any]:
        
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data

class RegForm(forms.Form):
    username = forms.CharField(label='用户名', 
                               max_length=30,
                               min_length=3,
                               widget=forms.TextInput(
                                attrs={'class':'form-control','placeholder':'请输入3-30长度的用户名'}))
    email = forms.CharField(label='邮箱', 
                            widget=forms.EmailInput(
                                attrs={'class':'form-control','placeholder':'请输入邮箱'}))
    password = forms.CharField(label='密码', 
                               min_length=6,
                               widget=forms.PasswordInput(
                                    attrs={'class':'form-control','placeholder':'请输入密码'}))
    password_again = forms.CharField(label='再输入一次密码', 
                                    min_length=6,
                                    widget=forms.PasswordInput(
                                        attrs={'class':'form-control','placeholder':'请再次输入密码'}))
    verification_code = forms.CharField(label='验证码',
                                    widget=forms.TextInput(
                                        attrs={'class':'form-control','placeholder':'点击"发送验证码"发送至邮箱'}
                                    ))
   
    def clean_username(self):
        username=self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username
    
    def clean_email(self):
        email=self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email
    
    def clean_password_again(self):
        password=self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password_again != password:
            raise forms.ValidationError('两次密码不一致')
        return password
    def clean(self):
        
        email = self.cleaned_data['email']
        code =cache.get(f'{email}', '')
        verification_code = self.cleaned_data.get('verification_code','')

        if code == '' or code != verification_code:
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data
    
class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(label='新的昵称',
                                   max_length = 20,
                                   widget=forms.TextInput(attrs={'class':'form-control', 'place-holder':'输入新的昵称'}))
    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
    
    def clean(self):
        #验证用户是否登录
        if self.user.is_authenticated:
           self.cleaned_data['user'] = self.user 
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data
    
class BindEmailForm(forms.Form):
    email = forms.EmailField(label='邮箱', 
                            widget=forms.EmailInput(
                                attrs={'class':'form-control','placeholder':'请输入邮箱'}))
    verification_code = forms.CharField(label='验证码',
                                    widget=forms.TextInput(
                                        attrs={'class':'form-control','placeholder':'点击"发送验证码"发送至邮箱'}
                                    ))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError
        return email
    
    def clean(self):
        #验证用户是否登录
        if self.request.user.is_authenticated:
           self.cleaned_data['user'] = self.request.user 
        else:
            raise forms.ValidationError('用户尚未登录')
        email = self.cleaned_data['email']
        code =cache.get(f'{email}', '')
        verification_code = self.cleaned_data.get('verification_code','')

        if code == '' or code != verification_code:
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data
    
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='旧的密码', 
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'placeholder':'请输入旧的密码'}
        )
    )
    new_password = forms.CharField(
        label='新的密码', 
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'placeholder':'请输入新的密码'}
        )
    )
    new_password_again = forms.CharField(
        label='请再次输入新的密码', 
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'placeholder':'请再次输入新的密码'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致')
        return self.cleaned_data

    def clean_old_password(self):
        # 验证旧的密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧的密码错误')
        return old_password
    
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class':'form-control', 'placeholder':'请输入绑定过的邮箱'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class':'form-control', 'placeholder':'点击“发送验证码”发送到邮箱'}
        )
    )
    new_password = forms.CharField(
        label='新的密码', 
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'placeholder':'请输入新的密码'}
        )
    )

    def clean(self):
        email = self.cleaned_data['email']
        code =cache.get(f'{email}', '')
        verification_code = self.cleaned_data.get('verification_code','')

        if code == '' or code != verification_code:
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在')
        return email