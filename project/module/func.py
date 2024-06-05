import os
import secrets,string,json
from line_bot_app.models import * #記得要改line_bot_app如果你和我不一樣
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from module.langchain_tool import *
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.tools import BaseTool
from openai import OpenAI
from django.conf import settings
from linebot import LineBotApi
from linebot.models import *
from urllib.parse import quote
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
GPT_MODEL = "gpt-3.5-turbo-0613"
client = OpenAI()#new
#6/3
#創建群組
def CreateGroup(groupname,user_id):
    letters = string.ascii_letters#產生英文字母
    digits = string.digits#產生字串
    # 如果有和資料庫重複會重新生成
    while True:
        secure_random_string = ''.join(secrets.choice(letters) + secrets.choice(digits) for i in range(15))#數字和英文字母串接
        if not GroupTable.objects.filter(group_code=secure_random_string).exists():
            break
    group_name = groupname
    group_code = secure_random_string
    try:
        #剛創建的群組加入資料庫
        unit = GroupTable(group_name=group_name, group_code=group_code)
        unit.save()
        #抓取群組的id且把資料加入到linking table中
        group = GroupTable.objects.get(group_id=unit.group_id)
        user_instance = PersonalTable.objects.get(line_id=user_id)
        try:
            unit3 = PersonalGroupLinkingTable.objects.create(personal=user_instance,group=group)
        except Exception as e:
            print(f"Error creating linking table record: {e}")
    except Exception as e:
        print(f"Error creating group: {e}")

#加入群組
def JoinGroup(mtext, user_id):
    code = mtext[6:]  # 取得井字號的後面
    #判斷使用者輸入有無此群組
    unit2 = GroupTable.objects.filter(group_code=code)
    if not unit2:
        return '查無此群組，請重新輸入'
    else:
        # 判斷使用者是否有想要重複加入群組，去linkingtable看有沒有重複加入
        group = GroupTable.objects.get(group_code=code)
        user_instance = PersonalTable.objects.get(personal_id=user_id)
        unit4 = PersonalGroupLinkingTable.objects.filter(personal=user_instance, group=group)
        if unit4:
            return '已經有加入該群組，若是要加入新群組請重新核對您的群組代碼'
        else:
            try:
                user_instance = PersonalTable.objects.get(personal_id=user_id)
                unit5 = PersonalGroupLinkingTable.objects.create(personal=user_instance,group=group)
                return '成功加入群組'
            except Exception as e:
                print(f"Error creating linking table record: {e}")
                return '加入群組時發生錯誤，請稍後再試'

#6/2
def classification(text,personal_id,transaction_type):
    #金額、地點、項目
    messages = []
    user_category_set_str =''
    pred_category=''
    return_data ={}
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": text})
    chat_response = get_payment_location_item(
        messages, tools=tools
    )
    assistant_message = chat_response.choices[0].message
    messages.append(assistant_message)
    tool_call = assistant_message.tool_calls[0].function.arguments
    data = json.loads(tool_call)
    payment = data.get("金額", "")
    location = data.get("地點", "")
    item = data.get("項目", "")
    #如果使用者有輸入項目，才丟到langchain裡面
    if item != '':
        user_category=PersonalCategoryTable.objects.filter(personal=personal_id,transaction_type=transaction_type)
        user_category_set=[]
        for category in user_category:
            category_name = category.category_name
            user_category_set.append(category_name)
        user_category_set_str = ', '.join(user_category_set)
        #類別
        agent = get_category_classification_tool(llm)
        data = agent(f"=使用者輸入：{text}，類別:{user_category_set_str}，ex:預測餐費就輸出餐費")['output']
        pred_category = str(data)
    #沒有的話就維持一樣空值
    else:
        item = item
    return_data = {
            'user_id':personal_id,
            'category': pred_category,
            'item': item,
            'payment':payment,
            'location':location,
            'transaction_type':transaction_type
        }
    return return_data

def get_payment_location_item(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e
tools= [
        {
            "type": "function",
            "function":{
                "name": "get_record_info",
                "description": """給了一個記帳資訊，請你幫我抓出地點、金額、項目
                """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "金額": {
                            "type": "string",
                            "description": "抓取金額，如果沒有抓到就為空值. e.g 200",
                        },
                        "地點": {
                            "type": "string",
                            "description": "抓取地點，如果沒有抓到就為空值. e.g 麥當勞、中央大學",
                        },
                        "項目": {
                            "type": "string",
                            "description": "抓取項目，如果沒有抓到就為空值. e.g 牛排、衣服、電影票",
                        },
                    },
                    "required":['金額',"地點","項目"]
                },
            },
        },
]
#6/2
def address_temporary(personal_id,item,payment,location,category,time):
    unit = PersonalCategoryTable.objects.get(personal_id=personal_id,category_name=category)
    category_id = unit.personal_category_id
    #從vue來是字串，但是資料庫為int所以這邊要轉型別，location和item就不用判斷因為資料庫存varchar
    if payment == '':
        payment = 0
    else:
        payment = int(payment)
    unit2 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=0,personal_id=personal_id,category_id=category_id)
    unit2.save()    

#6/2
def address_sure(personal_id,item,payment,location,category,time):
    unit = PersonalCategoryTable.objects.get(personal_id=personal_id,category_name=category)
    category_id = unit.personal_category_id
    unit2 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=1,personal_id=personal_id,category_id=category_id)
    unit2.save()    

# def sqlagent(text):