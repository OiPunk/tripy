import logging
import uuid

from fastapi import APIRouter
from starlette.requests import Request

from api.graph_api.graph_schemas import BaseGraphSchema, GraphRspSchema
from graph_chat.finally_graph import graph

# 创建分路由
router = APIRouter()

log = logging.getLogger('graph')


@router.post('/graph/', description='调用工作流', summary='调用工作流', response_model=GraphRspSchema)
def execute_graph(request: Request, obj_in: BaseGraphSchema):
    username = getattr(request.state, "username", "unknown")
    log.info("graph request user=%s", username)

    question = (obj_in.user_input or "").strip()
    if not question:
        return {'assistant': '请输入有效问题。'}

    default_config = {
        "configurable": {
            "passenger_id": "3442 587242",
            "thread_id": str(uuid.uuid4()),
        }
    }
    config = obj_in.config.model_dump() if obj_in.config else default_config

    result = ''  # AI助手的最后一条消息

    if question.lower() != 'y':  # 正常的用户提问
        events = graph.stream({'messages': ('user', question)}, config, stream_mode='values')
    else:  # 用户输入的是一个： y，表示确认
        events = graph.stream(None, config, stream_mode='values')

    for event in events:
        messages = event.get('messages')
        if messages:
            if isinstance(messages, list):
                message = messages[-1]  # 如果消息是列表，则取最后一个
            if message.__class__.__name__ == 'AIMessage':
                if message.content:
                    result = message.content  # 需要在Webui展示的消息

    current_state = graph.get_state(config)
    if current_state.next:  # 出现了工作流的中断
        result = "AI助手马上根据你要求，执行相关操作。您是否批准上述操作？输入'y'继续；否则，请说明您请求的更改。\n"

    return {'assistant': result}

