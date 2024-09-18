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
from pathlib import Path
import subprocess
from autogen.coding import LocalCommandLineCodeExecutor
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
# GPT_MODEL = "gpt-3.5-turbo-0613"
# client = OpenAI()#new
#6/3
#創建群組
def CreateGroup(groupname,user_id):
    letters = string.ascii_letters#產生英文字母
    digits = string.digits#產生字串
    # 如果有和資料庫重複會重新生成
    while True:
        secure_random_string = ''.join(secrets.choice(letters) + secrets.choice(digits) for i in range(4))#數字和英文字母串接
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
            unit15 = GroupCategoryTable(category_name = "飲料",transaction_type ='支出',group =unit)
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


def classification(text,personal_id):
    config_list = [{'model': 'gpt-4o','api_key': os.environ["OPENAI_API_KEY"],}]
    os.environ["OAI_CONFIG_LIST"] = json.dumps(config_list)
    # Create a user agent
    user = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={'use_docker':False}
    )
    category_list = []
    category = PersonalCategoryTable.objects.filter(personal_id = personal_id)
    for j in category:
        data2 = {
            "類別":j.category_name,
            "交易類型":j.transaction_type
        }
        category_list.append(data2)
    account_record = []
    account = PersonalAccountTable.objects.filter(personal_id = personal_id)
    for i in account:
        data3 = {
            "項目名稱":i.item,
            "類別":i.category.category_name,
            "交易類型":i.category.transaction_type
        }
        account_record.append(data3)
    format="[{\"項目名稱\":\"\"....(只能包含項目名稱、金額、地點、類別、交易類型)},{\"項目名稱\":\"\"....(只能包含項目名稱、金額、地點、類別、交易類型)}...]"
    # Create an assistant agent
    role ='''你是一個專業記帳助手，根據使用者的輸入抓取帳目要的參數，抓取以下參數，輸出格式須符合，不要輸出其他的格式。
                    參數：金額(若使用者有買多個要去算總金額，而其他的數字不是買的就不要理，只要輸出數字即可，若沒有抓取到金額請輸出0)、
                    地點(若沒有抓取到地點請輸出無)、項目名稱(若沒有抓取到項目名稱請輸出無)、交易類型、類別。
                   '''
    category_info = '''預測類別時，請先看"個人類別資料"，從使用者輸入內容中選擇最合適的一項"個人類別資料"的類別，如果無法從使用者的輸入判斷，
                    則若抓取的你抓取的項目名稱沒有在"帳目類別資料"，請自行選擇，若項目名稱有在"帳目類別資料"有相同就呈現該項目出現最多次的類別名稱
                    (例子:漢堡出現的類別，早餐有出現5次、晚餐有出現4次，那類別就抓取早餐)，若沒有最多次就輸出最好的結果，
                    請務必按照格式輸出，預測的類別必定是"個人類別資料"的其中之一的類別，不能輸出"個人類別資料"的內容以外的類別，請勿自行產生類別。
                    (例子:"個人類別資料"中有早餐、午餐、晚餐，預測的類別就只能是這三個其中之一，不能出現其他類別)
                '''
    examples = '''
              1.使用者輸入:買漢堡25，三明治15元。輸出:項目名稱:漢堡、金額:25、地點:無、類別：早餐、交易類型：支出，項目名稱:三明治、金額:15、地點:無、類別:午餐、交易類型:支出。
              2.使用者輸入:水果店買四個蘋果一個125元。輸出:項目名稱:蘋果、金額:500、地點:水果店、類別:水果、交易類型:支出。
              3.使用者輸入:薪水2000元。輸出:項目名稱:薪水、金額:2000、地點:無、類別：薪水、交易類型：收入。
              '''
    assistant = autogen.AssistantAgent(
        "assistant",
        # model
        llm_config={"config_list": config_list},
        system_message=role+category_info+"輸出格式："+format+"例子："+examples+"個人類別資料："+str(category_list)+"帳目類別資料："+str(account_record)
    )
    user_input=text
    agent = user.initiate_chat(assistant, message="使用者輸入："+user_input+"",summary_method="last_msg")
    result = agent.summary
    if result[:5] == 'ERROR':
        return "錯誤"
    else:
        result2 = agent.summary
        start_index = result2.find('[')
        end_index = result2.rfind(']') + 1
        extracted_content = result2[start_index:end_index]
        data_list = json.loads(extracted_content)
        return_data_list = []
    for data in data_list:
        return_data = {
            "item": data["項目名稱"],
            "payment": data["金額"],
            "location": data["地點"],
            "category": data['類別'],
            "transaction_type": data['交易類型']
        }
        # Print each processed result
        
        return_data_list.append(return_data)
    return return_data_list
#群組
def group_classification(text,group_id,personalID):
    config_list = [{'model': 'gpt-4o','api_key': os.environ["OPENAI_API_KEY"],}]
    os.environ["OAI_CONFIG_LIST"] = json.dumps(config_list)
    # Create a user agent
    user = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={'use_docker':False}
    )
    category_list = []
    category = GroupCategoryTable.objects.filter(group = group_id)
    for j in category:
        data2 = {
            "類別":j.category_name,
            "交易類型":j.transaction_type
        }
        category_list.append(data2)
    account_record = []
    account = GroupAccountTable.objects.filter(group = group_id)
    for i in account:
        data3 = {
            "項目名稱":i.item,
            "類別":i.category.category_name,
            "交易類型":i.category.transaction_type
        }
        account_record.append(data3)
    format="{\"項目名稱\":\"\"....(只能包含項目名稱、金額、地點、類別、交易類型、分帳人)}"
    # Create an assistant agent
    role ='''你是一個專業記帳助手，根據使用者的輸入抓取帳目要的參數，抓取以下參數，輸出格式須符合，不要輸出其他的格式。
                    參數：金額(若沒有抓取到金額請輸出0)、地點(若沒有抓取到地點請輸出無)、項目名稱(若沒有抓取到項目名稱請輸出無)、類別、交易類型、分帳人(包含分帳人和分帳金額，若使用者輸入沒有說明則設定成 "所有人")，請務必按照格式輸出。
                   '''
    category_info = '''預測類別時，請先看"群組類別資料"，從使用者輸入內容中選擇最合適的一項"群組類別資料"的類別，如果無法從使用者的輸入判斷，
                    則若抓取的你抓取的項目名稱沒有在"帳目類別資料"，請自行選擇，若項目名稱有在"帳目類別資料"有相同就呈現該項目出現最多次的類別名稱
                    (例子:漢堡出現的類別，早餐有出現5次、晚餐有出現4次，那類別就抓取早餐)，若沒有最多次就輸出最好的結果，
                    請務必按照格式輸出，預測的類別必定是"群組類別資料"的其中之一的類別，不能輸出"群組類別資料"的內容以外的類別，請勿自行產生類別。
                    (例子:"群組類別資料"中有早餐、午餐、晚餐，預測的類別就只能是這三個其中之一，不能出現其他類別)
                '''
    examples = '''
              1.使用者輸入:買漢堡25，三明治15元。輸出:項目名稱:漢堡、金額:25、地點:無、類別：早餐、交易類型：支出、分帳人：所有人，項目名稱:三明治、金額:15、地點:無、類別:午餐、交易類型:支出、分帳人：所有人。
              2.使用者輸入:水果店買四個蘋果一個125元，成員A除外。輸出:項目名稱;蘋果、金額:500、地點:水果店、類別:水果、交易類型:支出、分帳人：成員A除外。
              3.使用者輸入:薪水2000元。輸出:項目名稱:薪水、金額:2000、地點:無、類別：薪水、交易類型：收入。
              4.使用者輸入:飲料店買四杯飲料共400元，成員C和成員B除外。輸出:項目名稱:蘋果、金額:400、地點:飲料店、類別:飲料、交易類型:支出、分帳人：成員C和成員B除外。
              5.使用者輸入:聚餐$2000 我1000 楊雲杰500 王盛禾500。輸出:項目名稱:聚餐、金額:2000、地點:無、類別:娛樂、交易類型:支出、分帳人：我1000 楊雲杰500 王盛禾500。
              '''
    assistant = autogen.AssistantAgent(
        "assistant",
        # model
        llm_config={"config_list": config_list},
        system_message=role+category_info+"輸出格式："+format+"例子："+examples+"群組類別資料："+str(category_list)+"帳目類別資料："+str(account_record),
    )
    user_input=text
    agent = user.initiate_chat(assistant, message="使用者輸入："+user_input+"",summary_method="last_msg")
    result = agent.summary
    
    if result[:5] == 'ERROR':
        return "錯誤"
    else:
        result2 = agent.summary
        start_index = result2.find('{')
        end_index = result2.rfind('}') + 1
        extracted_content = result2[start_index:end_index]
        data = json.loads(extracted_content)
        return_data={
            "item":data["項目名稱"],
            "payment":data["金額"],
            "location":data["地點"],
            "category":data['類別'],
            "transaction_type":data['交易類型'],
            "member":data['分帳人']
        }
        return group_account_spliter(group_id,data['分帳人'],data["金額"],return_data,personalID)
    
def group_account_spliter(group_id,text,amount,account_data,personalID):
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
        max_consecutive_auto_reply=0,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={'use_docker':False}
    )
    format = '[{\'成員名稱\': \'\',\'分帳金額\':\'\'},(輸出的分帳人名字要和給予的名單一模一樣)'
    system_prompt = '給予群組的成員名單，從使用者的輸入判斷需要分帳的人和分帳金額並一一列出，分帳金額按照使用者的輸入判斷即可，若與抓分帳人無關的資訊請輸出ERROR，只會產生一筆結果，請務必按照格式輸出，無需輸出任何無關資訊'
    examples = '''假若群組內有小明、小美、小白，分帳總金額是3000 
            1.使用者輸入：小明、小美除外都要分帳。[{'成員名稱': '小白','分帳金額':3000}]。
            2.使用者輸入：全部人均分。[{'成員名稱': '小明','分帳金額':1000},{'成員名稱': '小美','分帳金額':1000},{'成員名稱': '小白','分帳金額':1000}]。
            3.使用者輸入：小明 1000 小美 1500 小白 500 。[{'成員名稱': '小明','分帳金額':1000},{'成員名稱': '小美','分帳金額':1500},{'成員名稱': '小白','分帳金額':500}]。
            4.使用者輸入：小明 1000 小美 1500 。[{'成員名稱': '小明','分帳金額':1000},{'成員名稱': '小美','分帳金額':1500},{'成員名稱': '剩餘的人','分帳金額':500}]。
            '''
    # Create an assistant agent
    assistant = autogen.AssistantAgent(
        "assistant",
        system_message=system_prompt+"輸出格式："+format+"例子:"+examples,
        llm_config={"config_list": config_list},
    )
    personal_info = PersonalTable.objects.get(personal_id=personalID)
    personal_name = personal_info.user_name
    agent = user.initiate_chat(assistant, message="輸入者："+personal_name+",分帳總金額："+str(amount)+",成員名單:"+str(personal_name_list)+",使用者輸入:"+text+"",summary_method="last_msg")
    result = agent.summary
    if result[:5] == 'ERROR':
        return "錯誤"
    else:
        result2 = agent.summary
        names = result2.strip().rstrip(',').split(',')
        split = [name.strip() for name in names]
        account_data['member']=result2
        return account_data
#暫存
def address_temporary(personal_id,item,payment,location,category,time,transaction_type):
    try:
        unit = PersonalCategoryTable.objects.get(personal=personal_id,transaction_type = transaction_type,category_name=category)
    except Exception as e:
        return 'no'
    category_id = unit.personal_category_id
        
    #從vue來是字串，但是資料庫為int所以這邊要轉型別，location和item就不用判斷因為資料庫存varchar
    payment = int(payment)
    unit2 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=0,personal_id=personal_id,category_id=category_id)
    unit2.save()    
    return 'ok'

#完成確認
def address_sure(personal_id,item,payment,location,category,time):
    try:
        unit = PersonalCategoryTable.objects.get(personal=personal_id,category_name=category)
    except Exception as e:
        return 'no'
    category_id = unit.personal_category_id
    unit2 = PersonalAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=1,personal_id=personal_id,category_id=category_id)
    unit2.save()    
    return 'ok'
#一般查詢
def sqlagent(text,personal_id):
    personal_info_list = []
    group_account_list = []
    split_return_list = []
    group = []
    personal_info = PersonalTable.objects.get(personal_id=personal_id)
    personal_account_info = PersonalAccountTable.objects.filter(personal=personal_info)
    #個人帳
    for i in personal_account_info:
        category_instance = i.category
        date=i.account_date.strftime('%Y-%m-%d') if i.account_date else None
        data = {
            # "個人帳目編號":i.personal_account_id,
            # '花費項目': i.item,
            # "記帳日期": i.account_date.strftime('%Y-%m-%d') if i.account_date else None,
            # '地點': i.location,
            # '金額': i.payment,
            # '資料完整flag': i.info_complete_flag,
            # '類別名稱': category_instance.category_name,
            # '交易類型': category_instance.transaction_type,
            str(i.item)+','+
            str(date)+','+
            str(i.location)+','+
            str(i.payment)+','+
            str(i.info_complete_flag)+','+
            str(category_instance.category_name)+','+
            str(category_instance.transaction_type)

        }
        personal_info_list.append(data)
    #群組帳    
    split_instance  = SplitTable.objects.filter(personal = personal_info)
    for k in split_instance:
        account = k.group_account_id
        group_table = GroupAccountTable.objects.filter(group_account_id = account)
        for i in group_table:
            group_name = i.group.group_name
            date = i.account_date.strftime('%Y-%m-%d') if i.account_date else None
            data3={
                # '群組帳目編號': i.group_account_id,
                # '花費項目': i.item,
                # "記帳日期": i.account_date.strftime('%Y-%m-%d') if i.account_date else None,
                # '地點': i.location,
                # '總付款金額': i.payment,
                # '群組名稱': group_name,
                # '資料完整flag': i.info_complete_flag,
                # '總付款人id':i.personal.personal_id,
                # '類別名稱': i.category.category_name,
                # '交易類型': i.category.transaction_type,
                str(i.group_account_id)+','+
                str(i.item)+','+
                str(date)+','+
                str(i.location)+','+
                str(i.payment)+','+
                str(group_name)+','+
                str(i.info_complete_flag)+','+
                str(i.personal.personal_id)+','+
                str(i.category.category_name)+','+
                str(i.category.transaction_type)
            }
            group_account_list.append(data3)

    # 分帳
    for m in split_instance:
        group_account = m.group_account
        split = SplitTable.objects.filter(group_account = group_account)
        for l in split:
            return_account = ReturnTable.objects.filter(split = l)
            for h in return_account:
                data4 = {
                    # '群組帳目編號':l.group_account.group_account_id,
                    # '分帳':l.payment,
                    # '還錢金額':h.return_payment,
                    # '欠款人':h.payer,
                    # '收款人':h.receiver,
                    # '還錢flag':h.return_flag,
                    str(l.group_account.group_account_id)+','+
                    str(l.payment)+','+
                    str(h.return_payment)+','+
                    str(h.payer)+','+
                    str(h.receiver)+','+
                    str(h.return_flag)
                }  
                split_return_list.append(data4) 
    group_link = PersonalGroupLinkingTable.objects.filter(personal = personal_info)
    for a in group_link:
        data5={
            "群組名稱":a.group.group_name
        }
        group.append(data5)
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
    system_prompt = '''你是一個帳目詢問助手，根據使用者的問題回答，根據給予你使用者的personal_id查詢他相關資料，若從給予的資料當中找到無關資訊請輸出ERROR，並且結尾就TERMINATE，有產生回答就直接TERMINATE
                    ，回答內容請務必精簡明瞭，必要資訊不能省略，如欠錢金額、使用者ID等，帳目資訊中的「個人帳目」：為個人的帳目資料，當中有一個欄位為資料完整flag(0為不完整，1為完整)，帳目資訊中的「群組帳目」、「群組」可以放在一起看：為群組帳目的資訊，當中有一個欄位為資料完整flag(0為不完整，1為完整)，帳目資訊中的「分帳資訊」：為群組分帳的金額，還錢flag(0為為還錢、1為還錢、2為收款人沒有確認也不算還錢)欠款人(欠別人錢的)，收款人(收別人錢的)
                    '''
    examples='''
        1.問題："我想查詢我2024年8月有幾筆未完整個人帳"：要加總個人帳目中的資料完整flag為0且日期為2024-08的帳目。
        2.問題："我想查詢2024年7月的收入減支出":抓取個人帳目中的資料完整flag為1且交易類型為支出且日期為2024-07進行加總與資料完整為1且交易類型為收入日期為2024-07進行加總，然後再支出減收入。
        3.問題："我想查詢我group1有幾筆未完整帳目"：抓取群組帳目，加總群組名稱為group1的資料完整flag為0的帳目筆數。
        4.問題："我在2024-05-27的group1中在中央大學付了多少錢"：總付款人id為該使用者，加總群組名稱為group1並且日期為2024-05-27且地點為中央大學且資料完整flag=1的金額)。
        5.問題："誰在group1有欠我錢"：抓取分帳帳目的群組帳目編號是多少去對到群組帳目裡面就可以知道群組名稱，所以群組名稱為group1，然後再看收款者是你，欠款者是其他人的，然後就可以分別呈現出來)
            '''
    assistant = autogen.AssistantAgent(
        "assistant",
        system_message=system_prompt+"例子："+examples,
        llm_config={"config_list": config_list},
    )
    account = "個人帳目格式:\{花費項目,記帳日期,地點,金額,資料完整flag,類別名稱,交易類型\}"+"個人帳目:"+str(personal_info_list)+"群組帳目格式:\{群組帳目編號,花費項目,記帳日期,地點,總付款金額,群組名稱,資料完整flag,總付款人id,類別名稱,交易類型\}"+"群組帳目:"+str(group_account_list)+"分帳帳目格式:\{群組帳目編號,分帳,還錢金額,欠款人,收款人,還錢flag\}"+"分帳帳目:"+str(split_return_list)+"群組:"+str(group)
    output=user.initiate_chat(assistant, message="我是:"+personal_info.user_name+"personal_id:"+personal_id+" 帳目資訊如下："+account+",問題:"+text,summary_method="last_msg")
    result = output.summary
    if result[:5] == 'ERROR':
        return "這問題與您的資訊無關，請重新詢問！"
    else:
        return result
#群組暫存
def address_group_temporary(group_id,item,payment,location,category,time,payer_id,shares,transaction_type):
    group_instance = GroupTable.objects.get(group_id=group_id)
    try:
        unit = GroupCategoryTable.objects.get(group=group_instance,transaction_type = transaction_type,category_name=category)
    except Exception as e:
        return 'no'
    category_id = unit.group_category_id
    #從vue來是字串，但是資料庫為int所以這邊要轉型別，location和item就不用判斷因為資料庫存varchar
    payment = int(payment)
    unit2 = GroupAccountTable(item=item,account_date=time,location=location,payment=payment,info_complete_flag=0,group = group_instance,category_id=category_id,personal_id=payer_id)
    unit2.save() 
    for share in shares:
        person = share['person']
        percentage = share['percentage']
        advance = share['advance_percentage']
        if advance == None:
            advance = 0
        else:
            advance = int(advance)
        unit_instance = PersonalTable(personal_id = person)
        unit4 = SplitTable(payment = percentage,advance_payment = advance,group_account = unit2,personal = unit_instance)
        unit4.save()
    return 'ok'
        
#群組完成
def address_group_sure(group_id,item,payment,location,category,time,payer_id,shares,transaction_type):
    group_instance = GroupTable.objects.get(group_id=group_id)
    try:
        unit = GroupCategoryTable.objects.get(group=group_instance,transaction_type = transaction_type,category_name=category)
    except Exception as e:
        return 'no'
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
        unit_instance = PersonalTable.objects.get(personal_id = person)
        unit4 = SplitTable(payment = percentage,advance_payment = advance,group_account = unit3,personal = unit_instance)
        unit4.save()
        #分帳
        should = unit4.payment
        should = int(should)
        pre  = unit4.advance_payment
        #分帳人的id和name
        spliter = unit4.personal.personal_id
        spliter_name = unit4.personal.user_name
        #總付款人的id和name
        total_payer = unit3.personal.personal_id
        total_payer_name = unit3.personal.user_name
        payer = spliter_name+" "+spliter
        receiver = total_payer_name+" "+total_payer
        if person != total_payer:
            if (should - pre)>0:
                pay = should - pre
                unit_return = ReturnTable(return_payment = pay,payer = payer,receiver =receiver,return_flag = 0,split = unit4)
                unit_return.save()
            elif (should - pre)<0:
                pay = pre - should 
                unit_return2= ReturnTable(return_payment = pay,payer = receiver,receiver=payer,return_flag = 0,split = unit4)
                unit_return2.save()
    return 'ok'
#拉人
def join_group(input,group_id):
    #判斷使用者輸入有無此群組
        personal = PersonalTable.objects.filter(personal_id = input)
        if not personal:
            return '查無此使用者，請重新輸入'
        else:
            user_instance = PersonalTable.objects.get(personal_id = input)
            group_instance =GroupTable.objects.get(group_id = group_id)
            unit4 = PersonalGroupLinkingTable.objects.filter(personal=user_instance, group=group_instance)
            if unit4:
                return '此使用者已加入該群組'
            else:
                unit5 = PersonalGroupLinkingTable.objects.create(personal=user_instance,group=group_instance)
                return '成功加入群組'

def new_group_category(group_id,transaction_type,category_name):
    #抓出哪個群組
    group_instance = GroupTable.objects.get(group_id=group_id)
    category = GroupCategoryTable.objects.filter(group = group_instance,transaction_type = transaction_type,category_name = category_name)
    if not category:
        unit = GroupCategoryTable(group = group_instance,transaction_type = transaction_type,category_name = category_name)
        unit.save()
        return "成功"
    else:
        return "已有該類別"
    
def change_group_cate(id,name):
    category_instance = GroupCategoryTable.objects.get(group_category_id=id)    
    # 更新 category_name
    category_instance.category_name = name
    # 保存更改
    category_instance.save()
    return "ok"
    
def new_personal_category(personal,transaction_type,category_name):
    personal_instance = PersonalTable.objects.get(personal_id = personal)
    category = PersonalCategoryTable.objects.filter(personal = personal_instance,transaction_type = transaction_type,category_name = category_name)
    if not category:
        unit = PersonalCategoryTable(personal = personal_instance,transaction_type = transaction_type,category_name = category_name)
        unit.save()
        return "成功"
    else:
        return "已有該類別"
def change_personal_cate(id,name):
    category_instance = PersonalCategoryTable.objects.get(personal_category_id=id)    
    # 更新 category_name
    category_instance.category_name = name
    # 保存更改
    category_instance.save()
    return "ok"

#畫圖
def drawplot(text,personal_id):
    personal_info_list = []
    personal_info = PersonalTable.objects.get(personal_id=personal_id)
    personal_account_info = PersonalAccountTable.objects.filter(personal=personal_info, info_complete_flag=1)
    #個人帳
    
    
    for i in personal_account_info:
        category_instance = i.category
        
        data = [i.item,i.account_date.strftime('%Y-%m-%d') if i.account_date else None,i.location,i.payment,category_instance.category_name,category_instance.transaction_type]
        personal_info_list.append(data)
    save_personal_info_to_file(personal_id)

    config_list = [
        {
            'model': 'ft:gpt-3.5-turbo-0125:personal::9pzkFyXX',#ft:gpt-3.5-turbo-0613:personal::9pz0a2ep:ckpt-step-68
            'api_key': os.environ["OPENAI_API_KEY"],
        },
    ]
    os.environ["OAI_CONFIG_LIST"] = json.dumps(config_list)
    coder = autogen.AssistantAgent(
        name="coder",
        llm_config={
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
        },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
        code_execution_config={
            
            "executor": LocalCommandLineCodeExecutor(work_dir="coding",virtual_env_context=None),

        },
        system_message="你將要執行的資料視覺化任務，根據資料內容及任務需求選擇最適當的圖表(折線圖,長條圖,圓餅圖,...),並使用python的matplotlib套件產生程式碼,將結果儲存在account.png, 資料內容如下( ['項目名稱', '日期', '地點', '金額', '類別', '收入支出'] ) ,用 from data import data 取得資料並使用",
    )

    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={
            
            "executor": LocalCommandLineCodeExecutor(work_dir="coding",virtual_env_context=None),

        },

    )
    # the assistant receives a message from the user_proxy, which contains the task description
    chat_res = user_proxy.initiate_chat(
        coder,
        message=text,
        summary_method="reflection_with_llm",
    )

    def find_and_rename_py_file(folder_path, new_filename):

        folder_path = Path(folder_path)
        

        for file_path in folder_path.iterdir():
            if file_path.is_file() and file_path.name.startswith('tmp'):
                
                current_filename = file_path.name
                new_file_path = folder_path / new_filename
                
                
                file_path.rename(new_file_path)
                
                print(f"File '{current_filename}' renamed to '{new_filename}'.")


    folder_path = "coding"  
    new_filename = "task.py" 
    find_and_rename_py_file(folder_path, new_filename)
    script_path = r'C:\Users\user\PycharmProjects\line_bot\project\coding\run.py'

    try:
        # 執行 run.py 腳本
        result = subprocess.run(['python', script_path],
                            capture_output=True, text=True, shell=True)
        
        # 檢查執行結果
        if result.returncode == 0:
            print("run.py executed successfully.")
            print(result.stdout)
        else:
            print("run.py execution failed.")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"run.py execution failed: {e}")

def unfinish_address_temporary(account_id,item,payment,location,category,time,transaction_type,user_id):
    payment = int(payment)
    try:
        category_instance = PersonalCategoryTable.objects.get(personal = user_id ,transaction_type=transaction_type,category_name = category)
    except Exception as e:
        return 'no'
    account_instance = PersonalAccountTable.objects.get(personal_account_id = account_id)
    account_instance.item = item
    account_instance.payment=payment
    account_instance.location = location
    account_instance.category_id = category_instance.personal_category_id
    account_instance.account_date = time
    account_instance.save()
    return "ok"

def unfinish_address_sure(account_id,item,payment,location,category,time,transaction_type,user_id):
    payment = int(payment)
    try:
        category_instance = PersonalCategoryTable.objects.get(personal = user_id ,transaction_type=transaction_type,category_name = category)
    except Exception as e:
        return 'no'
    account_instance = PersonalAccountTable.objects.get(personal_account_id = account_id)
    account_instance.item = item
    account_instance.payment=payment
    account_instance.location = location
    account_instance.category_id = category_instance.personal_category_id
    account_instance.account_date = time
    account_instance.info_complete_flag = 1
    account_instance.save()
    return "ok"

def save_personal_info_to_file(personal_id):
    file_path=r"C:\Users\user\PycharmProjects\line_bot\project\coding\data.py"
    personal_info_list = []
    personal_info = PersonalTable.objects.get(personal_id=personal_id)
    personal_account_info = PersonalAccountTable.objects.filter(personal=personal_info, info_complete_flag=1)
    
    print(personal_id)
    
    for i in personal_account_info:
        category_instance = i.category
        data = [
            i.item,
            i.account_date.strftime('%Y-%m-%d') if i.account_date else None,
            i.location,
            i.payment,
            category_instance.category_name,
            category_instance.transaction_type
        ]
        personal_info_list.append(data)
    
    
    personal_info_list_str = repr(personal_info_list)
    

    file_content = f"""
data = {personal_info_list_str}
    """
    
   
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(file_content)

    print(f"{file_path}")


def group_unfinish_sure(group_account_id,payer,item,payment,location,transaction_type,category,group_id,time,shares):
    payment = int(payment)
    try:
        category_instance = GroupCategoryTable.objects.get(group = group_id,transaction_type=transaction_type,category_name = category)
    except Exception as e:
        return 'no'
    account_instance = GroupAccountTable.objects.get(group_account_id = group_account_id)
    account_instance.item = item
    account_instance.payment = payment
    account_instance.location = location
    account_instance.category_id = category_instance.group_category_id
    account_instance.account_date = time
    account_instance.perosnal_id = payer
    account_instance.info_complete_flag=1
    account_instance.save()
    unit3 = GroupAccountTable.objects.get(group_account_id = group_account_id)
    for share in shares:
        person = share['person']
        percentage = share['percentage']
        advance = share['advance_percentage']
        if advance == None:
            advance = 0
        else:
            advance = int(advance)
        unit_instance = PersonalTable.objects.get(personal_id = person)
        check = SplitTable.objects.filter(group_account = group_account_id,personal = unit_instance.personal_id)
        if not check:
            unit_instance = PersonalTable.objects.get(personal_id = person)
            unit4 = SplitTable(payment = percentage,advance_payment = advance,group_account = unit3,personal = unit_instance)
            unit4.save()
        #分帳
        should = unit4.payment
        should = int(should)
        pre  = unit4.advance_payment
        #分帳人的id和name
        spliter = unit4.personal.personal_id
        spliter_name = unit4.personal.user_name
        #總付款人的id和name
        total_payer = unit3.personal.personal_id
        total_payer_name = unit3.personal.user_name
        payer = spliter_name+" "+spliter
        receiver = total_payer_name+" "+total_payer
        if person != total_payer:
            if (should - pre)>0:
                pay = should - pre
                unit_return = ReturnTable(return_payment = pay,payer = payer,receiver =receiver,return_flag = 0,split = unit4)
                unit_return.save()
            elif (should - pre)<0:
                pay = pre - should 
                unit_return2= ReturnTable(return_payment = pay,payer = receiver,receiver=payer,return_flag = 0,split = unit4)
                unit_return2.save()
    return 'ok'

def group_unfinish_temporary(group_account_id,payer,item,payment,location,transaction_type,category,group_id,time,shares):
    payment = int(payment)
    group_instance = GroupTable.objects.get(group_id=group_id)
    try:
        unit = GroupCategoryTable.objects.get(group=group_instance,transaction_type = transaction_type,category_name=category)
    except Exception as e:
        return 'no'
    #從vue來是字串，但是資料庫為int所以這邊要轉型別，location和item就不用判斷因為資料庫存varchar
    account_instance = GroupAccountTable.objects.get(group_account_id = group_account_id)
    account_instance.item = item
    account_instance.payment = payment
    account_instance.location = location
    account_instance.category_id = unit.group_category_id
    account_instance.account_date = time
    account_instance.perosnal_id = payer
    account_instance.save()
    unit5 = GroupAccountTable.objects.get(group_account_id = group_account_id)
    for share in shares:
        person = share['person']
        percentage = share['percentage']
        advance = share['advance_percentage']
        if advance == None:
            advance = 0
        else:
            advance = int(advance)
        unit_instance2 = PersonalTable.objects.get(personal_id = person)
        check = SplitTable.objects.filter(group_account = unit5.group_account_id,personal = unit_instance2.personal_id)
        if not check:
            unit_instance = PersonalTable.objects.get(personal_id = person)
            unit4 = SplitTable(payment = percentage,advance_payment = advance,group_account = unit5,personal = unit_instance)
            unit4.save()
    return 'ok'

def address_remove_spliter(group_account_id,shares):
    check = SplitTable.objects.get(group_account=group_account_id,personal = shares)
    check.delete()
        
