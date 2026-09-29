from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
import math
import requests
import os 
from typing import Any



load_dotenv()

## If you have openAI API key and want to use OpenAI models, uncomment the line below and comment the Gemini LLM initialization

# llm = ChatOpenAI()

# LLM 
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)



load_dotenv()


# LLM 
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)



# Tools

search_tool = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="advanced"
)

import math
from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """
    Powerful calculator for mathematical expressions.

    Supports:
    - Basic arithmetic: +, -, *, /, //, %, **
    - Powers and roots
    - Trigonometry
    - Logarithms and exponentials
    - Factorials
    - GCD and LCM
    - Min, max, sum, abs, round
    - Mathematical constants pi and e
    - Degree-based trigonometry

    Examples:
    2 + 2
    10 * 5
    2 ** 10
    sqrt(144)
    sin(pi / 2)
    log(100, 10)
    factorial(5)
    gcd(48, 18)
    20% of 500
    """

    try:
        expression = expression.strip()

        if not expression:
            return "Calculation error: Empty expression."

        expression = expression.replace("^", "**")

        if "%" in expression and " of " in expression.lower():
            expression = expression.lower().replace("% of ", " / 100 * ")

        allowed = {
            # Constants
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,

            # Basic
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,

            # Powers / roots
            "sqrt": math.sqrt,
            "pow": pow,

            # Trigonometry - radians
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "atan2": math.atan2,

            # Trigonometry - degrees
            "sind": lambda x: math.sin(math.radians(x)),
            "cosd": lambda x: math.cos(math.radians(x)),
            "tand": lambda x: math.tan(math.radians(x)),

            # Logarithms
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "ln": math.log,

            # Exponential
            "exp": math.exp,

            # Rounding
            "floor": math.floor,
            "ceil": math.ceil,

            # Number theory
            "factorial": math.factorial,
            "gcd": math.gcd,
            "lcm": math.lcm,

            # Combinations / permutations
            "comb": math.comb,
            "perm": math.perm,

            # Other
            "degrees": math.degrees,
            "radians": math.radians,
        }

        result = eval(
            expression,
            {"__builtins__": {}},
            allowed
        )

        if isinstance(result, float):
            if math.isnan(result):
                return "Calculation error: Result is NaN."

            if math.isinf(result):
                return "Calculation error: Result is infinite."

            result = round(result, 12)

        return str(result)

    except ZeroDivisionError:
        return "Calculation error: Division by zero."

    except ValueError as e:
        return f"Calculation error: Invalid mathematical value. {e}"

    except TypeError as e:
        return f"Calculation error: Invalid argument. {e}"

    except SyntaxError:
        return "Calculation error: Invalid mathematical expression."

    except Exception as e:
        return f"Calculation error: {str(e)}"


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=9MZO2JUBR7IFNTOI"
    r = requests.get(url)
    return r.json()



@tool
def get_current_weather(location: str) -> str:
    """
    Get the current real-time weather for a given city or location.

    Args:
        location: City or location name, for example:
                  "Dhaka", "London, UK", or "New York, US".

    Returns:
        A formatted current weather report.
    """

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return (
            "Weather API key is missing. "
            "Set the OPENWEATHER_API_KEY environment variable."
        )

    try:
        # Step 1: Convert the location name into latitude and longitude
        geocoding_url = "https://api.openweathermap.org/geo/1.0/direct"

        geocoding_params = {
            "q": location,
            "limit": 1,
            "appid": api_key,
        }

        geo_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10,
        )
        geo_response.raise_for_status()

        locations: list[dict[str, Any]] = geo_response.json()

        if not locations:
            return f"Could not find the location: {location}"

        latitude = locations[0]["lat"]
        longitude = locations[0]["lon"]
        resolved_name = locations[0].get("name", location)
        country = locations[0].get("country", "")
        state = locations[0].get("state", "")

        # Step 2: Get current weather using latitude and longitude
        weather_url = "https://api.openweathermap.org/data/2.5/weather"

        weather_params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10,
        )
        weather_response.raise_for_status()

        weather_data = weather_response.json()

        temperature = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        pressure = weather_data["main"]["pressure"]
        description = weather_data["weather"][0]["description"]
        wind_speed = weather_data.get("wind", {}).get("speed", "N/A")
        visibility_meters = weather_data.get("visibility")

        visibility_km = (
            round(visibility_meters / 1000, 1)
            if visibility_meters is not None
            else "N/A"
        )

        location_parts = [resolved_name]

        if state:
            location_parts.append(state)

        if country:
            location_parts.append(country)

        display_location = ", ".join(location_parts)

        return (
            f"Current weather in {display_location}:\n"
            f"- Condition: {description.title()}\n"
            f"- Temperature: {temperature}°C\n"
            f"- Feels like: {feels_like}°C\n"
            f"- Humidity: {humidity}%\n"
            f"- Pressure: {pressure} hPa\n"
            f"- Wind speed: {wind_speed} m/s\n"
            f"- Visibility: {visibility_km} km"
        )

    except requests.Timeout:
        return "The weather service request timed out. Please try again."

    except requests.HTTPError as error:
        status_code = error.response.status_code if error.response else "unknown"

        if status_code == 401:
            return "The OpenWeather API key is invalid or inactive."

        return f"Weather API returned an HTTP error: {status_code}"

    except requests.RequestException as error:
        return f"Could not connect to the weather service: {error}"

    except (KeyError, TypeError, ValueError) as error:
        return f"Unexpected weather API response: {error}"
    


# Make tool list
tools = [search_tool,calculator, get_stock_price,get_current_weather]

# Make the LLM tool-aware
llm_with_tools = llm.bind_tools(tools)




# State
class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]



# Nodes 1
def chat_node(state: ChatState):
    #take user query from state
    messages = state['messages']
    # send to llm
    response = llm_with_tools.invoke(messages)
    # response store state
    return {'messages': [response]}

# Nodes 2 - tool node
tool_node = ToolNode(tools)



# Checkpointer
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpoint = SqliteSaver(conn)



# graph
graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)
graph.add_node('tools', tool_node)

#add edges
graph.add_edge(START, 'chat_node')
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpoint)



# Helper functions for Streamlit frontend
def get_all_threads():
    all_threads = set()
    for ckpt in checkpoint.list(None):
        all_threads.add(ckpt.config['configurable']['thread_id'])

    return list(all_threads)



