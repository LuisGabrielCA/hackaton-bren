from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolExecutor
from langchain_openai import ChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_function
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage
from langgraph.prebuilt import ToolInvocation
import json
from langchain_core.messages import FunctionMessage
from langgraph.graph import StateGraph, END
import re

from dictionary import produtos

from dotenv import load_dotenv
import os

load_dotenv()

def searchProductsAndRelations(productName=None):
    if not productName:
        return produtos
    
    found_product = None
    produtos_relacionados = []
    for produto in produtos:
        if productName.lower() in produto['nome'].lower():
            produtos_relacionados = [p for p in produtos if p['id'] in produto['produtos_relacionados']]
            found_product = produto
            break
    
    if found_product is None:
        return (), produtos_relacionados
    else:
        return found_product, produtos_relacionados

tools = [TavilySearchResults(max_results=1)]
tool_executor = ToolExecutor(tools)
model = ChatOpenAI(temperature=0, streaming=False)

functions = [convert_to_openai_function(t) for t in tools]
model = model.bind_functions(functions)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def should_continue(state):
    messages = state['messages']
    last_message = messages[-1]
    if "function_call" not in last_message.additional_kwargs:
        return "end"
    else:
        return "continue"

def call_model(state, model):
    messages = state['messages']
    last_message = messages[-1].content if isinstance(messages[-1], HumanMessage) else ""
    
    matchProduct = re.search(r"\bcomprar\b\s+(o|a|os|as|um|uns| )?\s*(.*)", last_message, re.IGNORECASE)

    listProducts = re.search(r"liste|listar", last_message, re.IGNORECASE)

    if listProducts:
        produto= searchProductsAndRelations()
        product = f"Liste os produtos por nome e preco: {produto}"
        response = model.invoke(product)
        return {"messages": [response]}

    
    if matchProduct:
        nome_produto = matchProduct.group(2).strip()
        produto, produtos_relacionados = searchProductsAndRelations(nome_produto)
        
        if produto:
            info_produto = f"Deixe o texto mais detalhado: O {produto['nome']} esta sendo vendido atualmente por R${produto['preco']:.2f} "
            if produtos_relacionados:
                info_produto += " Você também pode se interessar por: " + ", ".join([f"{p['nome']} por R${p['preco']:.2f}" for p in produtos_relacionados])
            response = model.invoke([HumanMessage(content=info_produto)])
        else:
            response = model.invoke(messages)
    else:
        response = model.invoke(messages)
    
    return {"messages": [response]}

def call_tool(state):
    messages = state['messages']
    last_message = messages[-1]
    action = ToolInvocation(
        tool=last_message.additional_kwargs["function_call"]["name"],
        tool_input=json.loads(last_message.additional_kwargs["function_call"]["arguments"]),
    )
    response = tool_executor.invoke(action)
    function_message = FunctionMessage(content=str(response), name=action.tool)
    return {"messages": [function_message]}

workflow = StateGraph(AgentState)

workflow.add_node("agent", lambda state: call_model(state, model))
workflow.add_node("action", call_tool)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END
    }
)

workflow.add_edge('action', 'agent')

app = workflow.compile()

def process_text(mensagem):
    inputs = {"messages": [HumanMessage(content=mensagem)]}
    output = app.invoke(inputs)

    if output['messages'][1].additional_kwargs:
        return output['messages'][3].content

    return output['messages'][1].content
