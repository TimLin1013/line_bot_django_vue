import os
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent

db = SQLDatabase.from_uri("mysql+mysqlconnector://root:123456789@localhost:3306/test_db")
os.environ["OPENAI_API_KEY"] = ''
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

User_input="我買了綠豆冰沙"

agent_executor.invoke(
    "列出所有{類別,類別的子類別}，並判斷{"+User_input+"}這段敘述屬於哪一個{類別,類別的子類別}，答案必須包含一個類別和一個子類別"
)
