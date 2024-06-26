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
from line_bot_app import mail
import json
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def get_line_id_by_name(name):
    try:
        person = PersonalTable.objects.get(user_name=name)
        return person.line_id
    except Exception as e:
        print("Error retrieving user by name:", str(e))
        return None

#6/25
@csrf_exempt
@require_http_methods(["POST"])
def mark_as_paid(request):
    try:
        data = json.loads(request.body)
        return_id = data['return_id']

        account = ReturnTable.objects.get(return_id=return_id)
        account.return_flag = '1'
        account.save()

        # 從名字獲取line_id
        receiver_line_id = get_line_id_by_name(account.receiver)
        if receiver_line_id:
            receiver_message = f"{account.payer} 已歸還款項給你。"
            mail(receiver_line_id, receiver_message)
            print("Account marked as paid successfully.")
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Receiver LINE ID not found'}, status=404)

    except ReturnTable.DoesNotExist:
        print("Account not found.")
        return JsonResponse({'success': False, 'error': 'Account not found'}, status=404)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

#6/22
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_personal_expense_data(request):
    if request.method == "OPTIONS":
        return HttpResponse(status=204)  # To handle pre-flight requests if needed

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            account_date = data.get('account_date')
            personal_id = data.get('personal_id')

            # 拆分 account_date 以獲取年份和月份
            year, month = account_date.split('-')

            # 查詢該用戶在指定月份的賬本數據
            accounts = PersonalAccountTable.objects.filter(
                personal_id=personal_id,
                account_date__year=year,
                account_date__month=month
            ).values('item', 'payment', 'category_name', 'account_date', 'location')

            accounts_list = list(accounts)  # 將查詢結果轉換為字典列表

            return JsonResponse({'accounts': accounts_list}, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def get_group_expense_data(request):
    try:
        data = json.loads(request.body)
        group_id = data['group_id']
        account_date = data['account_date']
        expenses = GroupAccountTable.objects.filter(
            group_id=group_id,
            account_date__year=account_date[:4],  # First four characters are the year
            account_date__month=account_date[5:7]  # Characters 6 and 7 are the month
        ).values('item', 'payment', 'category_name', 'account_date')  # Include necessary fields

        account_list = list(expenses)
        return JsonResponse({"accounts": account_list}, safe=False)

    except KeyError as e:
        return JsonResponse({'error': str(e) + ' is missing'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#6/21
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_payback(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            personal_id = data.get('personal_id')

            # 加入群組名稱的查詢
            group_links = PersonalGroupLinkingTable.objects.filter(personal=personal_id)
            group_names = {link.group.group_id: link.group.group_name for link in group_links}

            # 使用 ReturnTable 模型來檢索還錢通知數據
            payback_notifications = ReturnTable.objects.filter(payer=personal_id)
            payer_payback_list = []
            for payback in payback_notifications:
                group_name = group_names.get(payback.split.group_account.group.group_id, "無群組")  # 從分帳表中找到群組名稱
                payback_data = {
                    "return_id": payback.return_id,
                    "return_payment": payback.return_payment,
                    "payer": payback.payer,
                    "receiver": payback.receiver,
                    "return_flag": payback.return_flag,
                    "group_name": group_name  # 加入群組名稱
                }
                payer_payback_list.append(payback_data)

            payback_notifications2 = ReturnTable.objects.filter(receiver=personal_id)
            receiver_payback_list = []
            for payback in payback_notifications2:
                group_name = group_names.get(payback.split.group_account.group.group_id, "無群組")  # 從分帳表中找到群組名稱
                payback_data = {
                    "return_payment": payback.return_payment,
                    "payer": payback.payer,
                    "receiver": payback.receiver,
                    "return_flag": payback.return_flag,
                    "group_name": group_name  # 加入群組名稱
                }
                receiver_payback_list.append(payback_data)

            response_data = {
                "message": "Data received successfully",
                "payer_payback_list": payer_payback_list,
                "receiver_payback_list": receiver_payback_list
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
        except PersonalTable.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': '支持POST請求'}, status=405)




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
                    user_id = event.source.user_id
                    personal = PersonalTable.objects.get(line_id = user_id)
                    personal_id = personal.personal_id
                    if mtext == "查詢":
                        line_bot_api.reply_message(event.reply_token, TextMessage(text="請輸入想問的帳目問題"))
                    else:
                        result = func.sqlagent(mtext,personal_id)
                        line_bot_api.reply_message(event.reply_token, TextMessage(text=result))
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


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
                    virtual_personal= ''.join(secrets.choice(letters) + secrets.choice(digits) for i in range(3))#數字和英文字母串接
                    if not PersonalTable.objects.filter(personal_id=virtual_personal).exists():
                        break
                #預設類別
                unit2 = PersonalTable(personal_id=virtual_personal,user_name=user_name,line_id=user_id)
                unit2.save()
                unit3 = PersonalCategoryTable(category_name = "早餐",transaction_type ='支出',personal =unit2)
                unit4 = PersonalCategoryTable(category_name = "午餐",transaction_type ='支出',personal =unit2 )
                unit5 = PersonalCategoryTable(category_name = "晚餐",transaction_type ='支出',personal =unit2 )
                unit6 = PersonalCategoryTable(category_name = "宵夜",transaction_type ='支出',personal =unit2 )
                unit7 = PersonalCategoryTable(category_name = "點心",transaction_type ='支出',personal =unit2 )
                unit8 = PersonalCategoryTable(category_name = "交通",transaction_type ='支出',personal =unit2 )
                unit9 = PersonalCategoryTable(category_name = "娛樂",transaction_type ='支出',personal =unit2 )
                unit10 = PersonalCategoryTable(category_name = "醫療",transaction_type ='支出',personal =unit2)
                unit11 = PersonalCategoryTable(category_name = "薪水",transaction_type ='收入',personal =unit2 )
                unit12 = PersonalCategoryTable(category_name = "付房租",transaction_type ='收入',personal =unit2 )
                unit13 = PersonalCategoryTable(category_name = "房租",transaction_type ='支出',personal =unit2 )
                unit14 = PersonalCategoryTable(category_name = "購物",transaction_type ='支出',personal =unit2)
                unit15 = PersonalCategoryTable(category_name = "無",transaction_type ='無',personal =unit2)
                unit3.save()
                unit4.save()
                unit5.save()
                unit6.save()
                unit7.save()
                unit8.save()
                unit9.save()
                unit10.save()
                unit11.save()
                unit12.save()
                unit13.save()
                unit14.save()
                unit15.save()
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
                    "category_name": category_name,
                    "group_name":"個人帳本"
                }
                account_list.append(account_data)
            #把那個人的peronsal_id抓出來，因為空白的表單需要peronsal_id
            personal = PersonalTable.objects.get(line_id = user_id)
            personal_id = personal.personal_id
            response_data = {
                "message": "Data received successfully",
                "accounts": account_list,
                "personal_id":personal_id,
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
            data = json.loads(request.body.decode('utf-8'))
            input_text = data.get('user_input')
            response_data = {'message': '成功接收數據','input': input_text}
            temp = func.classification(input_text)
            return JsonResponse({**response_data,'temp':temp})
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_group_account_info(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            #input_text = data.get('user_input')
            input_text2 = data.get('user_input2')
            if input_text2 == '':
                temp2 = []
            group_id = data.get('group_id')
            response_data = {'message': '成功接收數據'}
            #temp = func.classification(input_text)
            temp2 = func.group_account_spliter(group_id,input_text2)
            #temp['group_id'] = group_id
            return JsonResponse({**response_data,'temp2':temp2})
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_group_account_info_classificaiton(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            input_text = data.get('user_input')
            group_id = data.get('group_id')
            print(group_id)
            response_data = {'message': '成功接收數據'}
            temp = func.classification(input_text)
            if temp != '錯誤':
                temp['group_id'] = group_id
            return JsonResponse({**response_data,'temp':temp})
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
#暫存
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
            item = data.get('item')
            payment = data.get('payment')
            location = data.get('location')
            if data.get('category') == '':
                category='無'
            else:
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
#完成確認
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
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def joingroup(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            personal_id = data.get("Personal_ID")
            group_code = data.get("GroupCode")
            response_data = func.JoinGroup(personal_id,group_code)
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
#傳遞個人類別
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def returncategory(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            #在資料庫裡面的類別抓到前端去
            data = json.loads(request.body.decode('utf-8'))
            personal_id = data.get('personal_id')
            user_instance = PersonalTable.objects.get(personal_id=personal_id)
            user_category = PersonalCategoryTable.objects.filter(personal=user_instance)
            category_list=[]
            for category in user_category:
                category_name = category.category_name
                transaction_type = category.transaction_type
                category_data={
                    "category_name":category_name,
                    "transaction_type":transaction_type
                }
                category_list.append(category_data)
            response_data={
                "category":category_list
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
#傳遞群組類別
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def return_group_category(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            #在資料庫裡面的類別抓到前端去
            data = json.loads(request.body.decode('utf-8'))
            group_id = data.get('group_id')
            group_instance = GroupTable.objects.get(group_id=group_id)
            group_category = GroupCategoryTable.objects.filter(group=group_instance)
            category_list=[]
            for category in group_category:
                category_name = category.category_name
                transaction_type = category.transaction_type
                category_data={
                    "category_name":category_name,
                    "transaction_type":transaction_type
                }
                category_list.append(category_data)
            response_data={
                "category":category_list
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_group(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            personal_id = data.get('personal_id')

            user_instance = PersonalTable.objects.get(personal_id=personal_id)
            group_instances = PersonalGroupLinkingTable.objects.filter(personal=user_instance)
            group_list = []
            for group_link in group_instances:
                group_instance = group_link.group
                group_data = {
                    "group_id": group_instance.group_id,
                    "group_name": group_instance.group_name
                }
                group_list.append(group_data)

            response_data = {
                "message": "Data received successfully",
                "groups": group_list,
                "user_id": personal_id,
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
def get_group_account(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            personal_id = data.get('personal_id')
            group_account_list= [] 
            user_instance = PersonalTable.objects.get(personal_id= personal_id)
            group_instances = PersonalGroupLinkingTable.objects.filter(personal=user_instance)
            group_account_list = []
            for group_link in group_instances:
                group_instance = group_link.group
                group_account_instance= GroupAccountTable.objects.filter(group = group_instance)
                for group_account in group_account_instance:
                    group_account_data = {
                        "group_account_id": group_account.group_account_id,
                        "group_account_item": group_account.item,
                        "flag": group_account.info_complete_flag,
                        "account_date": group_account.account_date.strftime(
                        '%Y-%m-%d') if group_account.account_date else None,
                        "payment":group_account.payment,
                        "category_name":GroupCategoryTable.objects.get(group_category_id=group_account.category_id).category_name,
                        "group_id":group_account.group_id
                        
                    }
                    group_account_list.append(group_account_data)
                
                

            response_data = {
                "message": "Data received successfully",
                "group_account": group_account_list,
                "user_id": personal_id,
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
#報表個人資料
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def personal_report(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            #抓取前端傳來的參數date和personal_id
            personal_id = data.get('personal_id')
            date = data.get('date')
            date = str(date)
            income_total=0
            expense_total=0
            split_total=0
            #把income和expense的資料抓出來
            income_accounts = PersonalAccountTable.objects.filter(personal=personal_id,info_complete_flag=1 ,category__transaction_type='收入',account_date__startswith = date)
            expense_accounts = PersonalAccountTable.objects.filter(personal=personal_id,info_complete_flag=1, category__transaction_type='支出',account_date__startswith = date)
            split_accounts = SplitTable.objects.filter(personal = personal_id)
            
            #收入加起來
            for income in income_accounts:
                temp = income.payment
                income_total += temp
            #支出加起來
            for expense in expense_accounts:
                temp2 = expense.payment
                expense_total += temp2
            #群組分帳之後的加起來
            for split in split_accounts:
                temp3 = split.payment
                split_total += temp3
            expense_total = expense_total + split_total
            response_data = {
                "message": "Data received successfully",
                "income_total": income_total,
                "expense_total":expense_total
            }
            print(response_data)
            return JsonResponse(json.dumps(response_data), safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
     
#報表群組資料
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def group_report(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            #抓取前端傳來的參數date和group_id
            date = data.get('date')
            group_id = data.get('group_id')
            income_total=0
            expense_total=0
            #把income和expense的資料抓出來
            income_accounts = GroupAccountTable.objects.filter(group=group_id, category__transaction_type='收入',account_date__startswith = date)
            expense_accounts = GroupAccountTable.objects.filter(group=group_id, category__transaction_type='支出',account_date__startswith = date)
            #把每筆資料的payment加起來
            for income in income_accounts:
                temp = income.payment
                income_total += temp
            for expense in expense_accounts:
                temp2 = expense.payment
                expense_total += temp2
            response_data = {
                "message": "Data received successfully",
                "income_total": income_total,
                "expense_total":expense_total
            }
            return JsonResponse(json.dumps(response_data), safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
#抓成員
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def catch_member(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            #抓取前端傳來的參數group_id
            group_id = data.get('group_id')
            group_instance = GroupTable.objects.get(group_id=group_id)
            group_member = PersonalGroupLinkingTable.objects.filter(group=group_instance)
            personal_name_list=[]
            for member in group_member:
                personal_instance = member.personal
                personal_name = personal_instance.user_name
                personal_id = personal_instance.personal_id
                existing_names = [info["personal_name"] for info in personal_name_list]
                if personal_name in existing_names:
                    personal_info={
                        "personal_name":personal_name + "" +personal_id,
                        "personal_id":personal_id
                    }
                else:
                    personal_info={
                        "personal_name":personal_name,
                        "personal_id":personal_id
                    }
                personal_name_list.append(personal_info)
            response_data = {
                "personal_name_list":personal_name_list
            }
            return JsonResponse(json.dumps(response_data), safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_group_keep_temporary(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            group_id = data.get('group_id')
            payer_id = data.get('payer')
            item = data.get('item')
            payment = data.get('payment')
            location = data.get('location')
            category = data.get('category')
            if data.get('category') == '':
                category='無'
            else:
                category = category.get('category_name')
            time = data.get('time')
            time = datetime.fromisoformat(time)
            time += timedelta(hours=8)
            shares = data.get('shares')
            func.address_group_temporary(group_id,item,payment,location,category,time,payer_id,shares)
            response_data ='成功接收數據'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
     
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def get_group_keep_sure(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            group_id = data.get('group_id')
            payer_id = data.get('payer')
            item = data.get('item')
            payment = data.get('payment')
            location = data.get('location')
            category = data.get('category')
            if data.get('category') == '':
                category='無'
            else:
                category = category.get('category_name')
            time = data.get('time')
            time = datetime.fromisoformat(time)
            time += timedelta(hours=8)
            shares = data.get('shares')
            func.address_group_sure(group_id,item,payment,location,category,time,payer_id,shares)
            response_data ='成功接收數據'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def delete_personal(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            personal_id = data.get('personal_id')
            account_id = data.get('account_id')
            account = PersonalAccountTable.objects.get(personal_account_id = account_id, personal=personal_id)
            account.delete()
            
            return HttpResponse(json.dumps('成功'), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def delete_group(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response['Allow'] = 'POST, OPTIONS'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            group_id = data.get('group_id')
            account_id = data.get('account_id')
            account = GroupAccountTable.objects.get(group_account_id = account_id, group=group_id)
            account.delete()
            
            return HttpResponse(json.dumps('成功'), content_type="application/json")
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)