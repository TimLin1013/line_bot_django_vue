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
from langchain_community.utilities import SQLDatabase
from langchain.chains.openai_tools import create_extraction_chain_pydantic
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import List
from langchain.chains import create_sql_query_chain
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
# from langchain.agents import AgentType
# from langchain_community.utilities import SQLDatabase
# from langchain.agents.agent_toolkits import SQLDatabaseToolkit
# from langchain.llms.openai import OpenAI
# from langchain.chat_models import ChatOpenAI
# from langchain_community.agent_toolkits import create_sql_agent
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
                    user_id = event.source.user_id
                    personal = PersonalTable.objects.get(line_id = user_id)
                    personal_id = personal.personal_id
                    if mtext == "查詢":
                        line_bot_api.reply_message(event.reply_token, TextMessage(text="請輸入想問的帳目問題"))
                    else:
                        result = sqlagent(mtext,personal_id)
                        line_bot_api.reply_message(event.reply_token, TextMessage(text=result))
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
                    virtual_personal= ''.join(secrets.choice(letters) + secrets.choice(digits) for i in range(5))#數字和英文字母串接
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
            personal_id = data.get('personal_id')
            input_text = data.get('user_input')
            response_data = {'message': '成功接收數據','input': input_text}
            temp = func.classification(input_text,personal_id)
            return JsonResponse({**response_data,'temp':temp})
        except json.JSONDecodeError:
            return JsonResponse({'error': '無效的JSON數據'}, status=400)
    else:
         return JsonResponse({'error': '支持POST請求'}, status=405)
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
            category = data.get('category')
            category = category.get('category_name')
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
            category = category.get('category_name')
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
            print("id :"+personal_id)
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
            user_instance = PersonalTable.objects.get(personal_id=personal_id)
            group_account = GroupAccountTable.objects.filter(personal=user_instance)
            #print("id :"+personal_id)
            group_account_list = []
            for account in group_account:
                group_instance=account.group
                category_instance=account.category
                group_account_data = {
                    "item": account.item,
                    "group_name": group_instance.group_name,
                    "account_date": account.account_date.strftime(
                        '%Y-%m-%d') if account.account_date else None,
                    "location":account.location,
                    "payment":account.payment,
                    "category_name":category_instance.category_name,
                    "flag":account.info_complete_flag,
                    "group_id":account.group_account_id
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
            #把income和expense的資料抓出來
            income_accounts = PersonalAccountTable.objects.filter(personal=personal_id,info_complete_flag=1 ,category__transaction_type='收入',account_date__startswith = date)
            expense_accounts = PersonalAccountTable.objects.filter(personal=personal_id,info_complete_flag=1, category__transaction_type='支出',account_date__startswith = date)
            #先把使用者所有的群組抓出來
            user_instance = PersonalTable.objects.get(personal_id=personal_id)
            group_instances = PersonalGroupLinkingTable.objects.filter(personal=user_instance)
            temp = 0
            temp2 = 0
            temp3 = 0
            records = []
            records2 = []
            group_account_income_ids = []
            group_account_expense_ids = []
            #然後有關於使用者所有的群組相關帳全部抓出來
            for group_instance in group_instances:
                group_table_instance = group_instance.group
                group_accounts = GroupAccountTable.objects.filter(group=group_table_instance)
                #這裡分的就是每筆群組帳收入還是支出，因為這樣抓是split_table需要連動到個人的報表
                for account in group_accounts:
                    category_instance = account.category
                    account_date =account.account_date
                    year_month = account_date.strftime('%Y-%m')
                    if category_instance.transaction_type == '收入' and year_month == date:
                        group_account_income_ids.append(account.group_account_id)
                    if category_instance.transaction_type =='支出' and  year_month == date:
                        group_account_expense_ids.append(account.group_account_id)
            #這裡就是抓收入和支出的資訊
            for group_account_id in group_account_income_ids:
                records.extend(SplitTable.objects.filter(group_account=group_account_id))
            records = records
            for group_account_id in group_account_expense_ids:
                records2.extend(SplitTable.objects.filter(group_account=group_account_id))
            #把每筆資料的payment加起來
            for income in income_accounts:
                temp = income.payment
                income_total += temp
            for record in records:
                temp2 = record.payment
                income_total += temp2
            for expense in expense_accounts:
                temp2 = expense.payment
                expense_total += temp2
            for record2 in records2:
                temp3 = record2.payment
                expense_total += temp3
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
                        "personal_name":personal_name + "id:" +personal_id,
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
def sqlagent(text,personal_id):
    db = SQLDatabase.from_uri("mysql+mysqlconnector://root:0981429209@localhost:3306/my_project")#要改你自己的
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    class Table(BaseModel):
        """Table in SQL database."""
        name: str = Field(description="MYSQL資料庫的table名稱.")
    system = """回傳所有關於使用者問題可能相關的SQL table. \
    The tables are:

    personal_info
    group_info
    """
    category_chain = create_extraction_chain_pydantic(Table, llm, system_message=system)
    category_chain.invoke({"input": text})
    def get_tables(categories: List[Table]) -> List[str]:
        tables = []
        for category in categories:
            if category.name == "personal_info":
                tables.extend(["personal_table","personal_category_table","personal_account_table","group_table","split_table","return_table","group_account_table"])
            elif category.name == "group_info":
                tables.extend(["personal_table", "group_table", "group_category_table","group_account_table","personal_group_linking_table","split_table","return_table"])
        return tables
    table_chain = category_chain | get_tables  
    table_chain.invoke({"input": text})

    query_chain = create_sql_query_chain(llm, db)
    table_chain = {"input": itemgetter("question")} | table_chain
    full_chain = RunnablePassthrough.assign(table_names_to_use=table_chain) | query_chain
    query = full_chain.invoke(
        {"question": text+"，使用者的personal_id:"+personal_id+"最後回答不要有括號和資料庫型別且用有邏輯方式回答"}
    )
    print(query)
    temp = db.run(query)
    return temp