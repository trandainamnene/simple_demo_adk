import requests
import os
import warnings
from typing import Dict, Any
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters
from typing import Optional
try:  
    from dotenv import load_dotenv
except ImportError:  
    load_dotenv = None  

if load_dotenv:
    load_dotenv()


# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}
def _geocode_city(city: str, country_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Bước 1: Dùng Geocoding API để chuyển tên thành phố → tọa độ (lat, lon)
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return None

    url = "http://api.openweathermap.org/geo/1.0/direct"
    query = city
    if country_code:
        query += f",{country_code}"

    params = {
        "q": query,
        "limit": 5,       # lấy tối đa 5 kết quả để chọn cái chính xác nhất
        "appid": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200 or not response.json():
            return None

        locations = response.json()
        # Ưu tiên chọn kết quả đầu tiên (thường là chính xác nhất), hoặc có state/country rõ ràng
        return locations[0]

    except Exception:
        return None


def get_current_weather(city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool chính: Lấy thời tiết hiện tại của một thành phố (hỗ trợ tiếng Việt).
    
    Args:
        city: Tên thành phố, có thể có dấu (ví dụ: "Hà Nội", "Đà Lạt", "Ho Chi Minh City")
        country_code: Mã quốc gia ISO 3166-1 alpha-2 (tùy chọn, ví dụ: "VN", "US", "FR")
                      Giúp tránh nhầm lẫn khi có nhiều thành phố cùng tên.
    
    Returns:
        dict với dữ liệu thời tiết đẹp + emoji
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "OPENWEATHER_API_KEY chưa được thiết lập trong file .env"
        }

    # Bước 1: Geocoding - lấy tọa độ
    location = _geocode_city(city, country_code)
    if not location:
        return {
            "status": "error",
            "message": f"Không tìm thấy thành phố: {city}. Hãy thử thêm mã quốc gia (ví dụ: Hà Nội,VN)"
        }

    lat = location["lat"]
    lon = location["lon"]
    city_name = location.get("local_names", {}).get("vi") or location.get("name") or city
    state = location.get("state", "")
    country = location.get("country", "")

    # Bước 2: Lấy dữ liệu thời tiết bằng tọa độ
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",    # độ C
        "lang": "vi"          # mô tả thời tiết bằng tiếng Việt
    }

    try:
        response = requests.get(weather_url, params=params, timeout=10)
        if response.status_code != 200:
            return {"status": "error", "message": "Lỗi khi lấy dữ liệu thời tiết từ OpenWeather"}

        data = response.json()

        # Xử lý mô tả thời tiết + emoji
        weather = data["weather"][0]
        description = weather["description"].capitalize()
        icon = weather["icon"]

        # Map icon → emoji (một số phổ biến)
        emoji_map = {
            "01d": "Nắng", "01n": "Trăng",
            "02d": "Có mây", "02n": "Có mây",
            "03d": "Mây", "03n": "Mây",
            "04d": "Nhiều mây", "04n": "Nhiều mây",
            "09d": "Mưa rào", "09n": "Mưa rào",
            "10d": "Mưa", "10n": "Mưa",
            "11d": "Giông", "11n": "Giông",
            "13d": "Tuyết", "13n": "Tuyết",
            "50d": "Sương mù", "50n": "Sương mù",
        }
        weather_emoji = emoji_map.get(icon, "Thời tiết")

        return {
            "status": "success",
            "city": city_name,
            "state": state or None,
            "country": country,
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": round(data["wind"]["speed"] * 3.6, 1),  # m/s → km/h
            "description": description,
            "emoji": weather_emoji,
            "icon_code": icon,
            "coordinates": {"lat": round(lat, 4), "lon": round(lon, 4)},
        }

    except Exception as e:
        return {"status": "error", "message": f"Lỗi kết nối: {str(e)}"}

def _build_mcp_toolsets() -> list[McpToolset]:
    """Create MCP toolsets (if creds are available)."""
    tools: list[McpToolset] = []
    exa_api_key = os.getenv("EXA_API_KEY")

    if not exa_api_key:
        warnings.warn(
            "EXA_API_KEY is not set. Skipping the Exa MCP toolset. "
            "Set the value in your environment or .env file to enable MCP.",
            stacklevel=1,
        )
        return tools

    tools.append(
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "exa-mcp-server"],
                    env={"EXA_API_KEY": exa_api_key},
                ),
                timeout=30,
            ),
            tool_name_prefix="exa",
        )
    )
    return tools


root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    description="Tells the current time in a specified city.",
    instruction=(
        "You are a helpful assistant. "
        "Prefer the 'get_current_time' tool, but you can also call MCP tools or get_current_weather to get weather"
        "when you need web context."
    ),
    tools=[get_current_weather , get_current_time, *_build_mcp_toolsets()],
)