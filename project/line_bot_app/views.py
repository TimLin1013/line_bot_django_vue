from django.shortcuts import render
import secrets,string
# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from urllib.parse import parse_qsl
from datetime import datetime, timedelta
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from line_bot_app.models import *
from module import func
import json
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
#6/2
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            if isinstance(event,MessageEvent):
                if isinstance(event.message,TextMessage):
                    mtext = event.message.text
                    if mtext == "查詢":
                        line_bot_api.reply_message(event.reply_token, TextMessage(text="請輸入想問的帳目問題"))
                    else:
                        print('OK')
                        # func.sqlagent(mtext)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

#6/2 
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_user_account(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response

    if request.method == 'POST':
        try:
            
            data = json.loads(request.body.decode('utf-8'))
            user_id = data.get('userId') 
            user_name = data.get('name')
            #判斷第一次進來官方帳號的人
            user = PersonalTable.objects.filter(line_id=user_id)
            if not user:
                letters = string.ascii_letters#產生英文字母
                digits = string.digits#產生字串
                # 如果有和資料庫重複會重新生成
                while True:
                    virtual_personal= ''.join(secrets.choice(letters) + secrets.choice(digits) for i in range(12))#數字和英文字母串接
                    if not PersonalTable.objects.filter(personal_id=virtual_personal).exists():
                        break
                unit2 = PersonalTable(personal_id=virtual_personal,user_name=user_name,line_id=user_id)
                unit2.save()
            #抓出資料到首頁上
            user_instance = PersonalTable.objects.get(line_id=user_id)
            user_account = PersonalAccountTable.objects.filter(personal=user_instance)
            account_list = []
            for account in user_account:
                category_instance = account.category
                category_name = category_instance.category_name if category_instance else None
                account_data = {
                    "personal_account_id": account.personal_account_id,
                    "item": account.item,
                    "account_date": account.account_date.strftime(
                        '%Y-%m-%d') if account.account_date else None,
                    "location": account.location,
                    "payment": account.payment,
                    "flag": account.info_complete_flag,
                    "personal_id": account.personal.personal_id,
                    "category_id": account.category.personal_category_id,
                    "category_name": category_name
                }
                account_list.append(account_data)
            #把那個人的peronsal_id抓出來，因為空白的表單需要peronsal_id
            personal = PersonalTable.objects.get(line_id = user_id)
            personal_id = personal.personal_id
            response_data = {
                "message": "Data received successfully",
                "accounts": account_list,
                "personal_id":personal_id
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON', status=400)
        except PersonalTable.DoesNotExist:
            return HttpResponse('User not found', status=404)
        except Exception as e:
            return HttpResponse(str(e), status=500)
    else:
        return HttpResponse('Only POST requests are allowed', status=405)
#6/1
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_user_account_info(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_id = data.get('userId')
            input_text = data.get('user_input')
            transaction_type = data.get('type')
            personal = PersonalTable.objects.get(line_id = user_id)
            personal_id = personal.personal_id
            response_data = {'message': '成功接收數據','input': input_text}
            temp = func.classification(input_text,personal_id,transaction_type)
            return JsonResponse({**response_data,'temp':temp})
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
#6/2
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_keep_temporary(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            personal_id = data.get('userID')
            print(personal_id)
            item = data.get('item')
            payment = data.get('payment')
            location = data.get('location')
            category = data.get('category')
            time = data.get('time')
            time = datetime.fromisoformat(time)
            time += timedelta(hours=8)
            func.address_temporary(personal_id,item,payment,location,category,time)
            response_data ='成功接收數據'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)

#6/2
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_keep_sure(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            personal_id = data.get('userID')
            item = data.get('item')
            payment = data.get('payment')
            location = data.get('location')
            category = data.get('category')
            time = data.get('time')
            time = datetime.fromisoformat(time)
            time += timedelta(hours=8)
            func.address_sure(personal_id,item,payment,location,category,time)
            response_data ='成功接收數據'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def creategroup(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            line_id = data.get("userId")
            group_name = data.get("GroupName")
            func.CreateGroup(group_name,line_id)
            response_data ='成功接收數據'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
     