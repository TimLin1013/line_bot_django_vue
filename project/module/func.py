import os
import secrets,string,json
from line_bot_app.models import * 
from langchain_openai import ChatOpenAI
from module.langchain_tool import *
from openai import OpenAI
from django.conf import settings
from linebot import LineBotApi
from linebot.models import *
import autogen
import re
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


def classification(text,personal_id):
    config_list = [{'model': 'gpt-3.5-turbo','api_key': os.environ["OPENAI_API_KEY"],}]
    os.environ["OAI_CONFIG_LIST"] = json.dumps(config_list)
    # Create a user agent
    user = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={'use_docker':False}
    )
    format="{\"項目名稱\":\"\"....(只能包含項目名稱,金額,地點)}"
    # Create an assistant agent
    assistant = autogen.AssistantAgent(
        "assistant",
        system_message="你是一個帳目產生器，根據使用者的輸入來產生帳目，要抓取的參數有：金額(若使用者有買多個要去算總金額，而其他的數字不是買的就不要理，若沒有抓取到請輸出0),地點(舉例：中央大學、電影院、餐廳等等，若沒有抓取到地點請輸出無)，項目名稱(若沒有抓取到項目名稱請輸出無)，輸出格式是"+format+"，若與抓取參數無關請輸出ERROR，並且結尾就TERMINATE，產生一筆資訊就TERMINATE",
        llm_config={"config_list": config_list},
    )
    user_input=text
    agent = user.initiate_chat(assistant, message="使用者輸入："+user_input+"",summary_method="last_msg")
    result = agent.summary
    if result[:5] == 'ERROR':
        return "錯誤"
    else:
        result2 = agent.summary
        data = json.loads(result2)
        return_data={
            "item":data["項目名稱"],
            "payment":data["金額"],
            "location":data["地點"],
            "category":'',
            "transaction_type":''
        }
        return return_data

def address_temporary(personal_id,item,payment,location,category,time):
    unit = PersonalCategoryTable.objects.get(personal=personal_id,category_name=category)
    category_id = unit.personal_category_id
    #從vue來是字串，但是資料庫為int所以這邊要轉型別，location和item就不用判斷因為資料庫存varchar
    if payment == '':
        payment = 0
    else:
        payment = int(payment)
    unit2 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=0,personal_id=personal_id,category_id=category_id)
    unit2.save()    


def address_sure(personal_id,item,payment,location,category,time):
    unit = PersonalCategoryTable.objects.get(personal=personal_id,category_name=category)
    category_id = unit.personal_category_id
    unit2 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=1,personal_id=personal_id,category_id=category_id)
    unit2.save()    
def sqlagent(text,personal_id):
    personal_info_list = []
    group_info_list = []
    group_account_list = []
    split_info_list = []
    return_info_list=[]
    personal_info = PersonalTable.objects.get(personal_id=personal_id)
    personal_category_info = PersonalCategoryTable.objects.filter(personal=personal_id)
    personal_account_info = PersonalAccountTable.objects.filter(personal=personal_info, category__in=personal_category_info)

    for i in personal_account_info:
        personal_instance = i.personal
        category_instance = i.category
        data = {
            '個人帳目編號': i.personal_account_id,
            '花費項目': i.item,
            "記帳日期": i.account_date.strftime('%Y-%m-%d') if i.account_date else None,
            '地點': i.location,
            '金額': i.payment,
            '資料完整flag(0為不完整、1為完整)': i.info_complete_flag,
            '個人id': personal_id,
            '使用者姓名': personal_instance.user_name,
            '類別id': category_instance.personal_category_id,
            '類別名稱': category_instance.category_name,
            '交易類型': category_instance.transaction_type,
        }
        personal_info_list.append(data)

    # 獲取個人群組鏈接
    linking_table = PersonalGroupLinkingTable.objects.filter(personal=personal_info)

    # 構建群組信息列表
    for j in linking_table:
        group_instance = j.group
        data2 = {
            '群組編號': group_instance.group_id,
            '群組名稱': group_instance.group_name,
            '群組代碼': group_instance.group_code,
        }
        group_info_list.append(data2)
        
    for k in linking_table:
        group_instance2 = k.group
        group_table = GroupAccountTable.objects.filter(group=group_instance2)
        for group in group_table:
            group_instance3 = group.group
            group_category = GroupCategoryTable.objects.get(group=group_instance3)
            data3 = {
                '群組帳目編號': group.group_account_id,
                '花費項目': group.item,
                "記帳日期": group.account_date.strftime('%Y-%m-%d') if group.account_date else None,
                '地點': group.location,
                '金額': group.payment,
                '群組id':group.group.group_id,
                '資料完整flag(0為不完整、1為完整)': group.info_complete_flag,
                '付款人id':group.personal.personal_id,
                '類別名稱': group_category.category_name,
                '交易類型': group_category.transaction_type,
            }
            group_account_list.append(data3)

    # 獲取拆帳信息
    split_info = SplitTable.objects.filter(personal=personal_id)

    for l in split_info:
        return_info = ReturnTable.objects.get(split=l.split_id)
        data4 = {
            '群組分帳編號': l.split_id,
            '我要付款的金額': l.payment,
            '已經付款的金額': l.advance_payment,
            '群組帳目id':l.group_account_id,
        }
        data5={
            '還錢編號': return_info.return_id,
            '還錢金額': return_info.return_payment,
            '付款人': return_info.payer,
            '收款人': return_info.receiver,
            '還錢flag(0為沒有還錢、1為還錢)': return_info.return_flag,
        }
        split_info_list.append(data4)
        return_info_list.append(data5)
    config_list = [
        {
            'model': 'gpt-4',
            'api_key':os.environ["OPENAI_API_KEY"],
        },
        ]
    os.environ["OAI_CONFIG_LIST"] = json.dumps(config_list)
    
    user = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"use_docker": False}
    )

    assistant = autogen.AssistantAgent(
        "assistant",
        system_message="你是一個帳目詢問器，回答時盡量完整、有邏輯不要輸出list名稱與個人與帳目等等的id，以下為各個list的詳細資訊，若與資料庫無關請輸出ERROR，並且結尾就TERMINATE，產生一筆資訊就TERMINATE",
        llm_config={"config_list": config_list},
    )
    account = str(personal_info_list)+str(group_info_list)+str(group_account_list)+str(split_info_list)+str(return_info_list)
    output=user.initiate_chat(assistant, message="帳目資訊如下："+account+",問題:"+text,summary_method="last_msg",)
    print(output.summary)
    return "OK"
    # db = SQLDatabase.from_uri("mysql+mysqlconnector://root:0981429209@localhost:3306/my_project")#要改你自己的
    # llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0)
    # text=text+"personal_id:"+personal_id
    # write_query = create_sql_query_chain(llm, db)
    # execute_query = QuerySQLDataBaseTool(db=db)
    # answer_prompt = PromptTemplate.from_template(
    #     """
    #      - 若問題與資料庫相關，則使用正確的 MySQL 語法查詢相關資料，請從給予的personal_id進行全面查詢，請考慮上下文關聯並給出合理的邏輯。
    #      - 若問題與資料庫無關，則使用繁體中文適當且有邏輯的知識來回答，然後不要輸出personal_id與資料庫table的名稱。

    # Question: {question}
    # SQL Query: {query}
    # SQL Result: {result}
    # Answer: """
    # )
    
    # answer = answer_prompt | llm | StrOutputParser()
    # chain = (
    #     RunnablePassthrough.assign(query=write_query).assign(
    #         result=itemgetter("query") | execute_query
    #     )| answer
    # )
    # data = chain.invoke({"question":text})
    # return data