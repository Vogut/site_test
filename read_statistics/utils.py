import datetime
from os import read
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum,ReadDetail
def get_read_num(request,obj):
    ct=ContentType.objects.get_for_model(obj)
    key=f'{ct.model}_{obj.pk}_read'
    if not request.COOKIES.get(key):
        readnum, _ = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()
        date = timezone.now()
        readDetail, _ =ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk,date=date)
        readDetail.read_num += 1
        readDetail.save()

    return key

def get_week_read_data(content_type):
    today = timezone.now().date()
    read_nums=[]
    dates=[]
    for i in range(6,-1,-1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        day_details = ReadDetail.objects.filter(content_type=content_type,date=date)
        result = day_details.aggregate(week_read_data=Sum('read_num')) 
        read_nums.append(result['week_read_data'] or 0)
    return dates, read_nums

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    return read_details[:7]

def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    return read_details[:7]