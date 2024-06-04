from langchain.tools import BaseTool
from langchain.agents import load_tools, initialize_agent,AgentType
class category_classification(BaseTool):
    name = "account_classification_tool"
    description = (
        """
        這是帳目分類器，請從使用者輸入和類別進行下列判斷
        "類別"：從使用者給予的類別當中的值進行挑選，一定要從中選出一個不能自己產生，只需要輸出類別就好
        """
    )

    def _run(self,
            類別: str = None,
             ):

        return(f"category:{類別}")

def get_category_classification_tool(llm):
    tools = [category_classification()]

    return initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        verbose=True)


def create_item_name_tool(llm):
    tools = [create_item_name()]

    return initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        verbose=True)

class create_item_name(BaseTool):
    name = "create_item_name_tool"
    description = (
        """
        這是一筆花費的花費項目名稱生成器，請根據使用者輸入，生成合適的花費名稱，例如漢堡、 衣服、薪水等等不用動詞也就是吃漢堡就漢堡就可以
        """
    )

    def _run(self,
             項目: str = None
             ):

        return (f"item:{項目}")