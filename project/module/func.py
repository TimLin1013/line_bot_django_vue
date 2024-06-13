import os
import secrets,string,json
from line_bot_app.models import * 
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from module.langchain_tool import *
from langchain.agents import AgentType
from pydantic import BaseModel
from openai import OpenAI
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from django.conf import settings
from typing import Any, List,Dict
from linebot import LineBotApi
from langchain.prompts.chat import ChatPromptTemplate
from linebot.models import *
from urllib.parse import quote
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
import os
from langchain_community.agent_toolkits import create_sql_agent
from operator import itemgetter
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
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
        secure_random_string = ''.join(secrets.choice(letters) + secrets.choice(digits) for i in range(8))#數字和英文字母串接
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
def JoinGroup(personal_id,group_code):
    #判斷使用者輸入有無此群組
    unit2 = GroupTable.objects.filter(group_code=group_code)
    if not unit2:
        return '查無此群組，請重新輸入'
    else:
        # 判斷使用者是否有想要重複加入群組，去linkingtable看有沒有重複加入
        group = GroupTable.objects.get(group_code=group_code)
        user_instance = PersonalTable.objects.get(personal_id=personal_id)
        unit4 = PersonalGroupLinkingTable.objects.filter(personal=user_instance, group=group)
        if unit4:
            return '已加入該群組，請重新核對您的群組代碼'
        else:
            try:
                user_instance = PersonalTable.objects.get(personal_id=personal_id)
                unit5 = PersonalGroupLinkingTable.objects.create(personal=user_instance,group=group)
                return '成功加入群組'
            except Exception as e:
                print(f"Error creating linking table record: {e}")
                return '加入群組時發生錯誤，請稍後再試'


def classification(text,personal_id,transaction_type):
    #金額、地點、項目
    messages = []
    #user_category_set_str =''
    #pred_category=''
    return_data ={}
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": text})
    try:
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
        return_data = {
            'category': '',
            'item': item,
            'payment':payment,
            'location':location,
            'transaction_type':transaction_type
        }
        return return_data
    except Exception as e:
        return "錯誤"
    # #如果使用者有輸入項目，才丟到langchain裡面
    # if item != '':
    #     user_category=PersonalCategoryTable.objects.filter(personal=personal_id,transaction_type=transaction_type)
    #     user_category_set=[]
    #     for category in user_category:
    #         category_name = category.category_name
    #         user_category_set.append(category_name)
    #     user_category_set_str = ', '.join(user_category_set)
    #     #類別
    #     agent = get_category_classification_tool(llm)
    #     data = agent(f"=使用者輸入：{text}，類別:{user_category_set_str}，ex:預測餐費就輸出餐費")['output']
    #     pred_category = str(data)
    # #沒有的話就維持一樣空值
    # else:
    #     item = item

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
                            "description": "抓取金額，如果沒有抓到就為空值. e.g:50,200,2000,50000",
                        },
                        "地點": {
                            "type": "string",
                            "description": "抓取地點，如果沒有抓到就為空值. e.g:麥當勞、中央大學、LA",
                        },
                        "項目": {
                            "type": "string",
                            "description": "抓取花費的項目，如果沒有抓到就為空值. e.g:牛排、衣服、電影票",
                        },
                    },
                    "required":['金額',"地點","項目"]
                },
            },
        },
]

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


def address_sure(personal_id,item,payment,location,category,time):
    unit = PersonalCategoryTable.objects.get(personal_id=personal_id,category_name=category)
    category_id = unit.personal_category_id
    unit2 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=1,personal_id=personal_id,category_id=category_id)
    unit2.save()    
    
# def get_all_accounts(id):
#         personal_account = list(PersonalAccountTable.objects.filter(personal=id))
#         group_account = list(GroupAccountTable.objects.filter(personal=id))
#         return_payer_account = list(ReturnTable.objects.filter(payer=id))
#         return_receiver_account = list(ReturnTable.objects.filter(receiver=id))
#         personal_group_linking = PersonalGroupLinkingTable.objects.filter(personal=id)
#         group_ids = personal_group_linking.values_list('group', flat=True)
#         group_account2 = list(GroupAccountTable.objects.filter(group__in=group_ids))
#         split_account = list(SplitTable.objects.filter(personal=id))
#         account_data=[]
#         group_data=[]
#         return_payer_data=[]
#         return_receiver_data=[]
#         split_data=[]
#         group_data2=[]
#         for account in personal_account:
#             account_data.append({
#                 "personal_account_id":account.personal_account_id,
#                 "item":account.item,
#                 "account_date":account.account_date,
#                 "location":account.location,
#                 "payment":account.payment,
#                 "info_complete_flag":account.info_complete_flag,
#                 "personal_id":account.personal.personal_id,
#                 "personal_categroy_id":account.category.personal_category_id,
#             })
#         for gaccount in group_account:
#             group_data.append({
#                 "group_account_id":gaccount.group_account_id,
#                 "item":gaccount.item,
#                 "account_date":gaccount.account_date,
#                 "location":gaccount.location,
#                 "payment":gaccount.payment,
#                 "info_complete_flag":gaccount.info_complete_flag,
#                 "group_id":gaccount.group.group_id,
#                 "group_categroy_id":gaccount.category.group_category_id,
#                 "personal_id":gaccount.personal.personal_id,
#             })
#         for payer in return_payer_account:
#             return_payer_data.append({
#                 "return_id":payer.return_id,
#                 "return_payment":payer.return_payment,
#                 "payer":payer.payer,
#                 "receiver":payer.receiver,
#                 "return_flag":payer.return_flag,
#                 "split_id":payer.split.split_id,
#             })
#         for receiver in return_receiver_account:
#             return_receiver_data.append({
#                 "return_id":receiver.return_id,
#                 "return_payment":receiver.return_payment,
#                 "payer":receiver.payer,
#                 "receiver":receiver.receiver,
#                 "return_flag":receiver.return_flag,
#                 "split_id":receiver.split.split_id,
#             })
#         for split in split_account:
#             split_data.append({
#                 "split_id":split.split_id,
#                 "payment":split.payment,
#                 "advance_payment":split.advance_payment,
#                 "group_account_id":split.group_account.group_account_id,
#                 "personal_id":split.personal.personal_id,
#             })
#         for gaccount2 in group_account2:
#             group_data2.append({
#                 "group_account_id":gaccount2.group_account_id,
#                 "item":gaccount2.item,
#                 "account_date":gaccount2.account_date,
#                 "location":gaccount2.location,
#                 "payment":gaccount2.payment,
#                 "info_complete_flag":gaccount2.info_complete_flag,
#                 "group_id":gaccount2.group.group_id,
#                 "group_categroy_id":gaccount2.category.group_category_id,
#                 "personal_id":gaccount2.personal.personal_id,
#             })
#         all_data = []
#         all_data.extend(account_data)
#         all_data.extend(group_data)
#         all_data.extend(return_payer_data)
#         all_data.extend(return_receiver_data)
#         all_data.extend(split_data)
#         all_data.extend(group_data2)

#         return all_data
    
def sqlagent(text,personal_id):
    db = SQLDatabase.from_uri("mysql+mysqlconnector://root:0981429209@localhost:3306/my_project")#要改你自己的
    llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0)
    text=text+"personal_id:"+personal_id
    write_query = create_sql_query_chain(llm, db)
    execute_query = QuerySQLDataBaseTool(db=db)
    answer_prompt = PromptTemplate.from_template(
        """
         - 若問題與資料庫相關，則使用正確的 MySQL 語法查詢相關資料，請從給予的personal_id進行全面查詢，請考慮上下文關聯並給出合理的邏輯。
         - 若問題與資料庫無關，則使用繁體中文適當且有邏輯的知識來回答，然後不要輸出personal_id與資料庫table的名稱。

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )
    
    answer = answer_prompt | llm | StrOutputParser()
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )| answer
    )
    data = chain.invoke({"question":text})
    return data