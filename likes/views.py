from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from .models import LikeCount, LikeRecord

def SuccessResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)

def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

# Create your views here.
def like_change(request):
    user = request.user
    if not user.is_authenticated:
        return ErrorResponse(400, '未登录')
    content_type = request.POST.get('content_type')
    obj_id = int(request.POST.get('obj_id'))
    
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=obj_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401, '对象不存在')
    is_like = request.POST.get('is_like')
    

    if is_like == 'true':
        like_record, created = LikeRecord.objects.get_or_create(content_type = content_type, object_id = obj_id, user = user)
        if created:
            #未点赞过
            like_count, _ = LikeCount.objects.get_or_create(content_type = content_type, object_id = obj_id)
            like_count.liked_num += 1
            like_count.save()
            return SuccessResponse(like_count.liked_num)
        else:
            #不能重复点赞
            return ErrorResponse(402, '你已经点赞过了')
    else:
        #取消点赞
        if LikeRecord.objects.filter(content_type = content_type, object_id = obj_id, user = user).exists():
            like_record = LikeRecord.objects.get(content_type = content_type, object_id = obj_id, user = user)
            like_record.delete()
            like_count,created = LikeCount.objects.get_or_create(content_type = content_type, object_id = obj_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save() 
                return SuccessResponse(like_count.liked_num)
            else:           
                return ErrorResponse(404, '数据错误')
        else:
            return ErrorResponse(403, '你还没点赞过')