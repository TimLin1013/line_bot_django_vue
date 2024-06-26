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
            unit3.save()
            #預設類別
            unit16 = GroupCategoryTable(category_name = "早餐",transaction_type ='支出',group =unit )
            unit4 = GroupCategoryTable(category_name = "午餐",transaction_type ='支出',group =unit)
            unit5 = GroupCategoryTable(category_name = "晚餐",transaction_type ='支出',group =unit)
            unit6 = GroupCategoryTable(category_name = "宵夜",transaction_type ='支出',group =unit)
            unit7 = GroupCategoryTable(category_name = "點心",transaction_type ='支出',group =unit )
            unit8 = GroupCategoryTable(category_name = "交通",transaction_type ='支出',group =unit)
            unit9 = GroupCategoryTable(category_name = "娛樂",transaction_type ='支出',group =unit )
            unit10 = GroupCategoryTable(category_name = "醫療",transaction_type ='支出',group =unit )
            unit11 = GroupCategoryTable(category_name = "薪水",transaction_type ='收入',group =unit)
            unit14 = GroupCategoryTable(category_name = "購物",transaction_type ='支出',group =unit)
            unit15 = GroupCategoryTable(category_name = "無",transaction_type ='無',group =unit)
            unit16.save()
            unit4.save()
            unit5.save()
            unit6.save()
            unit7.save()
            unit8.save()
            unit9.save()
            unit10.save()
            unit11.save()
            unit14.save()
            unit15.save()
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


def classification(text):
    config_list = [{'model': 'gpt-4o','api_key': os.environ["OPENAI_API_KEY"],}]
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

        system_message="你是一個帳目產生器，根據使用者的輸入來產生帳目，要抓取的參數有：金額(舉例：200,100元等等，若使用者有買多個要去算總金額，而其他的數字不是買的就不要理，只要輸出數字即可，若沒有抓取到金額請輸出0),地點(舉例：中央大學、電影院、餐廳等等，若沒有抓取到地點請輸出無)，項目名稱(舉例：漢堡、房租、薪水等等就是抓花費的項目或是收入的項目，若沒有抓取到項目名稱請輸出無)，輸出格式是"+format+"，若不符合格式就輸出ERROR，並且結尾就TERMINATE，產生一筆資訊就TERMINATE",

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
    
def group_account_spliter(group_id,text):
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
            }
        else:
            personal_info={
                "personal_name":personal_name,
            }
        personal_name_list.append(personal_info)
    config_list = [{'model': 'gpt-4o','api_key': os.environ["OPENAI_API_KEY"],}]
    os.environ["OAI_CONFIG_LIST"] = json.dumps(config_list)
    # Create a user agent
    user = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={'use_docker':False}
    )
    format = '\"人名\",......(輸出的分帳人名字要和給予的名單一模一樣)'
    # Create an assistant agent
    assistant = autogen.AssistantAgent(
        "assistant",
        system_message="會給予群組的成員名單，然後從使用者的輸入判斷需要分帳的人並一一列出，若使用者沒有輸入，代表不用進行分帳，輸出格式"+format+"，若與抓分帳人無關的資訊請輸出ERROR，產生一筆結果就輸出TERMINATE且TERMINATE",
        llm_config={"config_list": config_list},
    )
    agent = user.initiate_chat(assistant, message="成員名單:"+str(personal_name_list)+"使用者輸入:"+text+"",summary_method="last_msg")
    result = agent.summary
    if result[:5] == 'ERROR':
        return "錯誤"
    else:
        result2 = agent.summary
        names = result2.strip().rstrip(',').split(',')
        split = [name.strip() for name in names]
        return split
#暫存
def address_temporary(personal_id,item,payment,location,category,time):
    if category == "無" or '':
        unit = PersonalCategoryTable.objects.get(personal=personal_id,category_name='無')
        category_id = unit.personal_category_id
        payment = int(payment)
        unit3 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=0,personal_id=personal_id,category_id=category_id)
        unit3.save() 
    else:
        if personal_id is None:
            personal_id = "Unknown"
        if category is None:
            category = "Unknown"
        print(personal_id + "  " + category)
        unit = PersonalCategoryTable.objects.get(personal=personal_id,category_name=category)
        category_id = unit.personal_category_id
        
        #從vue來是字串，但是資料庫為int所以這邊要轉型別，location和item就不用判斷因為資料庫存varchar
        payment = int(payment)
        unit2 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=0,personal_id=personal_id,category_id=category_id)
        unit2.save()    

#完成確認
def address_sure(personal_id,item,payment,location,category,time):
    unit = PersonalCategoryTable.objects.get(personal=personal_id,category_name=category)
    category_id = unit.personal_category_id
    unit2 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=1,personal_id=personal_id,category_id=category_id)
    unit2.save()    
#一般查詢
def sqlagent(text,personal_id):
    personal_info_list = []
    group_info_list = []
    group_account_list = []
    split_return_list = []
    personal_info = PersonalTable.objects.get(personal_id=personal_id)
    personal_category_info = PersonalCategoryTable.objects.filter(personal=personal_id)
    personal_account_info = PersonalAccountTable.objects.filter(personal=personal_info, category__in=personal_category_info)
    #個人帳
    for i in personal_account_info:
        personal_instance = i.personal
        category_instance = i.category
        data = {
            "個人帳目編號":i.personal_account_id,
            '花費項目': i.item,
            "記帳日期": i.account_date.strftime('%Y-%m-%d') if i.account_date else None,
            '地點': i.location,
            '金額': i.payment,
            '資料完整flag(0為不完整、1為完整)': i.info_complete_flag,
            '使用者姓名': personal_instance.user_name,
            '類別名稱': category_instance.category_name,
            '交易類型': category_instance.transaction_type,
        }
        personal_info_list.append(data)
    linking_table = PersonalGroupLinkingTable.objects.filter(personal=personal_info)

    #群組帳
    for j in linking_table:
        group_instance = j.group
        data2 = {
            '群組編號': group_instance.group_id,
            '群組名稱': group_instance.group_name,
        }
        group_info_list.append(data2)
        
    for k in linking_table:
        group_instance2 = k.group
        group_category = GroupCategoryTable.objects.filter(group=group_instance2)
        group_table = GroupAccountTable.objects.filter(category__in = group_category)
        for group in group_table:
            group_category = group.category
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
    split_instance  = SplitTable.objects.filter(personal = personal_info)
    for m in split_instance:
        group_account = m.group_account
        split = SplitTable.objects.filter(group_account = group_account)
        for l in split:
            return_account = ReturnTable.objects.filter(split = l)
            for h in return_account:
                data4 = {
                    '還錢金額':h.return_payment,
                    '欠款人':h.payer,
                    '收款人':h.receiver,
                    '還錢flag':h.return_flag
                }  
                split_return_list.append(data4) 
    config_list = [
        {
            'model': 'gpt-4o',
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
        system_message="你是一個帳目詢問器，請全部看完給予的list，然後有邏輯且適當精簡去回答，並不要輸出list名稱與個人與帳目等等的id，還錢flag(0為未還錢、1為已經還錢)，若從給予的資料當中找到無關資訊請輸出ERROR，並且結尾就TERMINATE，有產生回答就直接TERMINATE",
        llm_config={"config_list": config_list},
    )
    account = str(personal_info_list)+str(group_info_list)+str(group_account_list)+str(split_return_list)
    output=user.initiate_chat(assistant, message="我是:"+personal_info.user_name+" 帳目資訊如下："+account+",問題:"+text,summary_method="last_msg")
    result = output.summary
    if result[:5] == 'ERROR':
        return "這問題與資料庫無關，請重新詢問！"
    else:
        return result
#群組暫存
def address_group_temporary(group_id,item,payment,location,category,time,payer_id,shares):
    group_instance = GroupTable.objects.get(group_id=group_id)
    if category == "無" or '':
        unit = GroupCategoryTable.objects.get(group=group_instance,category_name='無')
        category_id = unit.group_category_id
        payment = int(payment)
        unit3 = GroupAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=0,group = group_instance,category_id=category_id,personal_id=payer_id)
        unit3.save() 
        unit5 = GroupAccountTable.objects.get(group_account_id = unit3.group_account_id)
        for share in shares:
            person = share['person']
            percentage = share['percentage']
            advance = share['advance_percentage']
            if advance == None:
                advance = 0
            else:
                advance = int(advance)
            unit_instance = PersonalTable(personal_id = person)
            unit4 = SplitTable(payment = percentage,advance_payment = advance,group_account = unit5,personal = unit_instance)
            unit4.save()
    else:
        unit = GroupCategoryTable.objects.get(group=group_instance,category_name=category)
        category_id = unit.group_category_id
        #從vue來是字串，但是資料庫為int所以這邊要轉型別，location和item就不用判斷因為資料庫存varchar
        payment = int(payment)
        unit2 = GroupAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=0,group = group_instance,category_id=category_id,personal_id=payer_id)
        unit2.save() 
        unit5 = GroupAccountTable(group_account_id = unit2.group_account_id)
        for share in shares:
            person = share['person']
            percentage = share['percentage']
            advance = share['advance_percentage']
            if advance == None:
                advance = 0
            else:
                advance = int(advance)
            unit_instance = PersonalTable(personal_id = person)
            unit4 = SplitTable(payment = percentage,advance_payment = advance,group_account = unit5,personal = unit_instance)
            unit4.save()
        
#群組完成
def address_group_sure(group_id,item,payment,location,category,time,payer_id,shares):
    group_instance = GroupTable.objects.get(group_id=group_id)
    unit = GroupCategoryTable.objects.get(group=group_instance,category_name=category)
    category_id = unit.group_category_id
    #從vue來是字串，但是資料庫為int所以這邊要轉型別，location和item就不用判斷因為資料庫存varchar
    payment = int(payment)
    unit2 = GroupAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=1,group = group_instance,category_id=category_id,personal_id=payer_id)
    unit2.save() 
    unit3 = GroupAccountTable.objects.get(group_account_id = unit2.group_account_id)
    for share in shares:
        person = share['person']
        percentage = share['percentage']
        advance = share['advance_percentage']
        if advance == None:
            advance = 0
        else :
            advance = int(advance)
        unit_instance = PersonalTable(personal_id = person)
        unit4 = SplitTable(payment = percentage,advance_payment = advance,group_account = unit3,personal = unit_instance)
        unit4.save()
        #分帳
        should = unit4.payment
        pre  = unit4.advance_payment
        spliter = unit4.personal.personal_id
        total_payer = unit3.personal.personal_id
        if person != total_payer:
            if (should - pre)>0:
                pay = should - pre
                unit_return = ReturnTable(return_payment = pay,payer = spliter,receiver =total_payer,return_flag = 0,split = unit4)
                unit_return.save()
            elif (should - pre)<0:
                pay = pre - should 
                unit_return2= ReturnTable(return_payment = pay,payer = total_payer,receiver=spliter,return_flag = 0,split = unit4)
                unit_return2.save()
    
    