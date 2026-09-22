# making the tool , httpx to get the response from APIs from the internet

import httpx
from langchain_core.tools import tool

@tool
def get_weather (name:str) ->str :
    """this  a weather tool that is used to get the first the longitutes and lattitudes of 
      then using those to get the weather of the city you give it input the city name """
    print(f"using the get weather tool to find about {name}")
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={name}&count=1"
        print("using the url")
        response= httpx.get(geo_url , timeout=20).json()
        print("the httpx is being called ")
        if "results" not in response:
            print(f"cound not find the reponse in the result not found {response["results"]}")
            return f"could not find the the location of the city {name} , check if the name was correct "
        long= response["results"][0]["longitude"]
        lati=response["results"][0]["latitude"]

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lati}&longitude={long}&current_weather=true"
        weather_response= httpx.get(weather_url , timeout=10).json()

        if "current_weather" not in weather_response:
            return f"there was an error finding the weather "
        temp=weather_response["current_weather"]["temperature"]
        hum= weather_response["current_weather"]["windspeed"]
        print(f"the weathre in {name} is having temprature{temp} and humidity {hum}")

        return f"the weather in {name} is with a temprature {temp} and humidity {hum}"


    except Exception as e:
        return "an unknown error occur {e} "


# Making the agent 

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from  langgraph.graph import StateGraph , MessagesState , START , END
from langgraph.prebuilt import ToolNode , tools_condition
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv
load_dotenv()

llm =ChatOpenAI(model="gpt-5-nano")
llm_with_tools=llm.bind_tools([get_weather])

system_prompt= SystemMessage(content="you are an helpful assistant and speak in a nice way telling about weather however the reposne youget from the tool you can use it in yuor own words and also when user inputs the city correct the mispelling of the city , dont ever answer yourself of the weather tell using the tool ")


def chat_model(state:MessagesState)-> dict :
    messages=[system_prompt]+ state["messages"]

    response=llm_with_tools.invoke(messages)

    return {"messages":[response]}

builder=StateGraph(MessagesState)
builder.add_node("agent", chat_model)
builder.add_node("tools", ToolNode([get_weather]))

builder.add_edge(START , "agent")
builder.add_conditional_edges("agent" , tools_condition)
builder.add_edge("tools", "agent")
# builder.add_node("a")

memory=MemorySaver()


graph=builder.compile(checkpointer=memory)


def main():
    while True:
        try:
            user_query=input("enter the city you want to know about the weeather ")
        except (EOFError , KeyboardInterrupt):
            break

        config = {"configurable": {"thread_id": "my-first-agent-thread"}}

        response= graph.invoke(
            {"messages":[("user",user_query)]},
            config=config
        )

        agent_reply=response["messages"][-1].content
        print(f"\n Agent :{agent_reply}")


if __name__=="__main__":
    main()

    




        



    

