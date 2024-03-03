import copy
import json
from dotenv import dotenv_values
import os
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage
from langchain.schema.messages import (
    FunctionMessage,
)
from langchain.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import (
    create_openai_fn_chain,
)
from langchain.schema import (
    ChatGeneration,
    Generation,
    OutputParserException,
)
from typing import Any, List
from langchain.schema.output_parser import BaseGenerationOutputParser
import time

from . import OPENAI_API_KEY

class customOutputFunctionsParser(BaseGenerationOutputParser[Any]):
    """Parse an output that is one of sets of values."""
 
    strict: bool = False
    def parse_result(self, result: List[Generation]) -> Any:
        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            raise OutputParserException(
                "This output parser can only be used with a chat generation."
            )
        message = generation.message
        if ("function_call" in message.additional_kwargs):
            func_call = copy.deepcopy(message.additional_kwargs["function_call"])
            func_call["arguments"] = json.loads(func_call["arguments"], strict=self.strict)
            return {"Parsed_Function_Call":func_call, "Message":message.additional_kwargs}
        else:
            return  {"Message":message.content}

output_parser=customOutputFunctionsParser()


def run_llm_chain_once(prompt_with_one_input:ChatPromptTemplate,available_functions:dict,question:str,max_tokens:int=1000):
    
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model='gpt-3.5-turbo-0613',max_tokens=max_tokens)
    
    function_llm_chain = create_openai_fn_chain([v for v in available_functions.values()], llm, prompt_with_one_input,output_parser=output_parser,verbose=True)
    output=function_llm_chain.run(input=question)
    print(function_llm_chain.llm_kwargs)

    if 'function_call' in output["Message"]:
        function_name=output['Parsed_Function_Call']["name"]
        function_arguments=output['Parsed_Function_Call']["arguments"]
        if function_name in available_functions:
            try:
                retrieved_results=available_functions[function_name](**function_arguments)
            except:
                retrieved_results={"Erorr":"Wrong arguments passed"}

            prompt_with_one_input.extend([AIMessage(content=str(output["Message"]))])
            prompt_with_one_input.extend([FunctionMessage(content=str(retrieved_results),name=function_name)])
            
            #creating another chain but without including the function - to avoid  overusage of tokens
            llm_chain = LLMChain(llm=llm, prompt=prompt_with_one_input, verbose=True)
            try:
                final_answer=llm_chain.run(input=question)
            except Exception as Error:
                final_answer=Error

            print(final_answer)

            return {"Question":question,"Function_name":function_name,"Function_arguments":function_arguments,"answer":final_answer}
        else:
            return {"Question":question,"Function_name":function_name,"Function_arguments":function_arguments,"answer":"Wrong function called"}
    else:
        return {"Question":question,"Function_name":"","Function_arguments":"","answer":output["Message"]}
    
def run_llm_chain_more_than_once(prompt_with_one_input:ChatPromptTemplate,available_functions:dict,question:str,max_tokens:int=1000, sleepTimeBetweenCalls:int=30,noofcalls:int=5):
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model='gpt-3.5-turbo-0613',max_tokens=max_tokens)
    counter=0
    steps={"Question":question}
    steps["steps"]=[]
    function_llm_chain = create_openai_fn_chain([v for v in available_functions.values()], llm, prompt_with_one_input,output_parser=output_parser,verbose=True)
    output=function_llm_chain.run(input=question)
    print(function_llm_chain.llm_kwargs)

    while 'function_call' in output["Message"]:
        time.sleep(sleepTimeBetweenCalls)
        counter+=1
        try:
            function_name=output['Parsed_Function_Call']["name"]
            function_arguments=output['Parsed_Function_Call']["arguments"]
        except:
            steps["answer"]=output["Message"]
            break
        
        if function_name in available_functions:
            steps["steps"].append({"Function_name":function_name,"Function_arguments":function_arguments})
            try:
                retrieved_results=available_functions[function_name](**function_arguments)
            except:
                retrieved_results={"Erorr":"Wrong arguments passed"}
            prompt_with_one_input.extend([AIMessage(content=str(output["Message"]))])
            prompt_with_one_input.extend([FunctionMessage(content=str(retrieved_results),name=function_name)])
            try:
                output=function_llm_chain.run(input=question)
            except Exception as E:
                print(E)
                steps["answer"]="Wrong output from LLM"
                break
        else:
            steps["steps"].append({"Function_name":function_name,"Function_arguments":function_arguments})
            steps["answer"]="Wrong function called"
            break
        
        if counter==noofcalls:
            steps["answer"]="Too many function calls"
            break
        
       
    if "answer" not in steps:
        steps["answer"]=output["Message"]
    return steps