from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from urllib.parse import parse_qsl
from static import *

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from line_bot_app.models import *
from module import func
import json
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
##

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
            print(json.dumps(event, default=lambda o: o.__dict__, indent=4))  # 打印 event 内容
            if isinstance(event, MessageEvent):
                user_id = event.source.user_id  # 取得LINE ID
                profile = line_bot_api.get_profile(user_id)
                # 取得用戶名稱
                user_name = profile.display_name
                # 判斷使用者有無在personalTable裡面，沒有在裡面然後創建群組，這樣就有一個群組，但是personalTable卻沒有紀錄這個人
                user = PersonalTable.objects.filter(personal_id=user_id)
                if not user:
                    # 如果沒有就要加入到個人的table
                    unit2 = PersonalTable(personal_id=user_id, user_name=user_name)
                    unit2.save()
                if isinstance(event.message, TextMessage):
                    mtext = event.message.text
                    if mtext == '<我的帳本>':
                        print("OK")
                    elif mtext[:6] == '<建立群組>':
                        reply_message = func.CreateGroup(mtext, user_id)
                        line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_message))
                    elif mtext[:6] == '<加入群組>':
                        reply_message = func.JoinGroup(mtext, user_id)
                        line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_message))
                    elif mtext[:7] == '<使用者輸入>':
                        func.classfication(mtext[len('<使用者輸入>'):],user_id,"支出")
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
@csrf_exempt
def test(request):
    if request.method == 'POST':
  
        return HttpResponse(json.dumps("success"), content_type="application/json")
    else:
        return HttpResponse('Only GET requests are allowed', status=405)

def liff_add(request):
    if request.method == 'GET':
        return render(request, 'Line_liff_add.html')
def personal_account_form(request):#new
    if request.method == 'GET':
        return render(request, 'Line_liff_personal_form.html')




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


            user_instance = PersonalTable.objects.get(personal_id=user_id)
            user_account = PersonalAccountTable.objects.filter(personal=user_instance)

            account_list = []
            for account in user_account:
                category_instance = account.category
                category_name = category_instance.category_name if category_instance else None
                account_data = {
                    "personal_account_id": account.personal_account_id,
                    "item": account.item,
                    "account_date": account.account_date.strftime(
                        '%Y-%m-%d %H:%M:%S') if account.account_date else None,
                    "location": account.location,
                    "payment": account.payment,
                    "flag": account.flag,
                    "personal_id": account.personal.personal_id,
                    "category_id": account.category.personal_category_id,
                    "category_name": category_name
                }
                account_list.append(account_data)

            response_data = {
                "message": "Data received successfully",
                "accounts": account_list
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
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_user_account_info(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('userId')
            input_text = data.get('input')
            transaction_type = data.get('type')
            response_data = {'message': '成功接收數據', 'userId': user_id, 'input': input_text}
            temp = func.classification(input_text,user_id,transaction_type)
            return JsonResponse({**response_data,'temp':temp})
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)