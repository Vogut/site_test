import threading

from django.shortcuts import redirect, render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.urls import reverse
from django.utils.timezone import localtime
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Comment
from .forms import CommentForm
# Create your views here.

class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)
    
    def run(self):
        send_mail(
            self.subject, 
            '', 
            settings.EMAIL_HOST_USER, 
            [self.email], 
            fail_silently=self.fail_silently,
            html_message=self.text
        )


def update_comment(request):
    data={}
    comment_form = CommentForm(request.POST, user = request.user)
    if comment_form.is_valid():
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']
        parent = comment_form.cleaned_data['parent']
        print(parent)
        if not parent is None:
            comment.root = parent if parent.root is None else parent.root 
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()
        if comment.parent is None:
            # 评论我的博客
            subject = '有人评论你的博客'
            email = comment.content_object.get_email()
        else:
            # 回复评论
            subject = '有人回复你的评论'
            email = comment.reply_to.email
        if email != '':
            context = {}
            context['comment_text'] = comment.text
            context['url'] = comment.content_object.get_url()
            text = render_to_string('comment/send_mail.html', context)
            send_mail = SendMail(subject, text, email)
            send_mail.start()

        #返回数据
        data['status'] = 'success'
        data['username'] = comment.user.get_nickname_or_username
        data['comment_time'] = localtime(comment.comment_time).strftime('%Y-%m-%d %H:%M:%S')
        data['text'] = comment.text
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        if not parent is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username
        else:
            data['reply_to'] =''
        data['pk'] = comment.pk   
        data['root_pk'] = comment.root.pk if not comment.root is None else ''  
    else:
        data['status'] = 'error'
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)