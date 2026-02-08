from typing import List, Dict

import gradio as gr
import uuid

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from graph_chat.assistant import CtripAssistant, assistant_runnable, primary_assistant_tools
from graph_chat.base_data_model import ToFlightBookingAssistant, ToBookCarRental, ToHotelBookingAssistant, \
    ToBookExcursion
from graph_chat.build_child_graph import build_flight_graph, builder_hotel_graph, build_car_graph, \
    builder_excursion_graph
from tools.flights_tools import fetch_user_flight_information
from graph_chat.draw_png import draw_graph
from graph_chat.state import State
from tools.init_db import update_dates
from tools.tools_handler import create_tool_node_with_fallback, _print_event

# 定义了一个流程图的构建对象
builder = StateGraph(State)


def get_user_info(state: State):
    """
    获取用户的航班信息并更新状态字典。
    参数:
        state (State): 当前状态字典。
    返回:
        dict: 包含用户信息的新状态字典。
    """
    return {"user_info": fetch_user_flight_information.invoke({})}


# 新增：fetch_user_info节点首先运行，这意味着我们的助手可以在不采取任何行动的情况下看到用户的航班信息
builder.add_node('fetch_user_info', get_user_info)
builder.add_edge(START, 'fetch_user_info')

# 添加 四个业务助理 的 子工作流
builder = build_flight_graph(builder)
builder = builder_hotel_graph(builder)
builder = build_car_graph(builder)
builder = builder_excursion_graph(builder)

# 添加主助理
builder.add_node('primary_assistant', CtripAssistant(assistant_runnable))
builder.add_node(
    "primary_assistant_tools", create_tool_node_with_fallback(primary_assistant_tools)  # 主助理工具节点，包含各种工具
)


def route_primary_assistant(state: dict):
    """
    根据当前状态 判断路由到 子助手节点。
    :param state: 当前对话状态字典
    :return: 下一步应跳转到的节点名
    """
    route = tools_condition(state)  # 判断下一步的方向
    if route == END:
        return END  # 如果结束条件满足，则返回END
    tool_calls = state["messages"][-1].tool_calls  # 获取最后一条消息中的工具调用
    if tool_calls:
        if tool_calls[0]["name"] == ToFlightBookingAssistant.__name__:
            return "enter_update_flight"  # 跳转至航班预订入口节点
        elif tool_calls[0]["name"] == ToBookCarRental.__name__:
            return "enter_book_car_rental"  # 跳转至租车预订入口节点
        elif tool_calls[0]["name"] == ToHotelBookingAssistant.__name__:
            return "enter_book_hotel"  # 跳转至酒店预订入口节点
        elif tool_calls[0]["name"] == ToBookExcursion.__name__:
            return "enter_book_excursion"  # 跳转至游览预订入口节点
        return "primary_assistant_tools"  # 否则跳转至主助理工具节点
    raise ValueError("无效的路由")  # 如果没有找到合适的工具调用，抛出异常


builder.add_conditional_edges(
    'primary_assistant',
    route_primary_assistant,
    [
        "enter_update_flight",  # 航班 子助手的入口节点
        "enter_book_car_rental",  # 租车 子助手的入口节点
        "enter_book_hotel",  # 酒店 子助手的入口节点
        "enter_book_excursion",  # 旅游景点 子助手的入口节点
        "primary_assistant_tools",  # 主助手的工具： 全网搜索工具，查询企业政策的工具
        END,
    ]
)

builder.add_edge('primary_assistant_tools', 'primary_assistant')


# 每个委托的工作流可以直接响应用户。当用户响应时，我们希望返回到当前激活的工作流
def route_to_workflow(state: dict) -> str:
    """
    如果我们在一个委托的状态中，直接路由到相应的助理。
    :param state: 当前对话状态字典
    :return: 应跳转到的节点名
    """
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"  # 如果没有对话状态，返回主助理
    return dialog_state[-1]  # 返回最后一个对话状态


builder.add_conditional_edges("fetch_user_info", route_to_workflow)  # 根据获取用户信息进行路由

memory = MemorySaver()
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=[
        "update_flight_sensitive_tools",
        "book_car_rental_sensitive_tools",
        "book_hotel_sensitive_tools",
        "book_excursion_sensitive_tools",
    ]
)

#
# draw_graph(graph, 'graph4.png')

session_id = str(uuid.uuid4())
# update_dates()  # 每次测试的时候：保证数据库是全新的，保证，时间也是最近的时间

# 配置参数，包含乘客ID和线程ID
config = {
    "configurable": {
        # passenger_id用于我们的航班工具，以获取用户的航班信息
        "passenger_id": "3442 587242",
        # 检查点由session_id访问
        "thread_id": session_id,
    }
}


def execute_graph(chat_bot: List[Dict]) -> List[Dict]:
    """ 执行工作流的函数"""
    user_input = chat_bot[-1]['content']
    result = ''  # AI助手的最后一条消息

    if user_input.strip().lower() != 'y':  # 正常的用户提问
        events = graph.stream({'messages': ('user', user_input)}, config, stream_mode='values')
    else:  # 用户输入的是一个： y，表示确认
        events = graph.stream(None, config, stream_mode='values')

    for event in events:
        messages = event.get('messages')
        if messages:
            if isinstance(messages, list):
                message = messages[-1] # 如果消息是列表，则取最后一个
            if message.__class__.__name__ == 'AIMessage':
                if message.content:
                    result = message.content  # 需要在Webui展示的消息
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > 1500:
                msg_repr = msg_repr[:1500] + " ... （已截断）"  # 超过最大长度则截断
            print(msg_repr)  # 输出消息的表示形式

    current_state = graph.get_state(config)
    if current_state.next:  # 出现了工作流的中断
        result = "AI助手马上根据你要求，执行相关操作。您是否批准上述操作？输入'y'继续；否则，请说明您请求的更改。\n"

    chat_bot.append({'role': 'assistant', 'content': result})
    return chat_bot


def do_graph(user_input, chat_bot):
    """输入框提交后，执行的函数"""
    if user_input:
        chat_bot.append({'role': 'user', 'content': user_input})
    return '', chat_bot


css = '''
#bgc {background-color: #7FFFD4}
.feedback textarea {font-size: 24px !important}
'''
with gr.Blocks(title='携程AI智能助手', css=css) as instance:
    gr.Label('携程AI智能助手', container=False)

    chatbot = gr.Chatbot(type='messages', height=350, label='AI助手')  # 聊天记录组件

    input_textbox = gr.Textbox(label='请输入你的问题📝', value='')  # 输入框组件

    input_textbox.submit(do_graph, [input_textbox, chatbot], [input_textbox, chatbot]).then(execute_graph, chatbot,
                                                                                            chatbot)

if __name__ == '__main__':
    # 启动Gradio的应用
    instance.launch(debug=True)
