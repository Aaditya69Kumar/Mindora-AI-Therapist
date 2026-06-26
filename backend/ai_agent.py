from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from geopy.geocoders import Nominatim
import requests

from backend.tools import query_medgemma
from backend.config import GROQ_API_KEY


geolocator = Nominatim(user_agent="ai_therapist")


@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    General mental health support.
    """

    return query_medgemma(query)





@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Find therapists near a location.
    """

    try:

        loc = geolocator.geocode(location)

        if not loc:
            return f"Could not find location: {location}"

        lat = loc.latitude
        lon = loc.longitude

        query = f"""
        [out:json];
        (
          node["healthcare"="psychotherapist"](around:10000,{lat},{lon});
          node["amenity"="clinic"](around:10000,{lat},{lon});
          node["amenity"="hospital"](around:10000,{lat},{lon});
          node["healthcare"="counselling"](around:10000,{lat},{lon});
          node["healthcare"="therapist"](around:10000,{lat},{lon});
        );
        out;
        """

        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            headers={"User-Agent": "SafeSpace AI Therapist"},
            timeout=20
        )

        response.raise_for_status()

        try:
            data = response.json()
        except Exception as json_error:
            return f"Error parsing response from location service: {str(json_error)}"

        if not data.get("elements"):
            return f"No therapists found near {location}"

        output = [f"Therapists near {location}:"]

        for place in data["elements"][:5]:

            tags = place.get("tags", {})

            name = tags.get(
                "name",
                "Unknown"
            )

            phone = tags.get(
                "phone",
                "Phone unavailable"
            )

            street = tags.get(
                "addr:street",
                ""
            )

            city = tags.get(
                "addr:city",
                ""
            )

            output.append(
                f"- {name} | {street} {city} | {phone}"
            )

        return "\n".join(output)

    except Exception as e:

        return f"Location search failed: {str(e)}"


tools = [
    ask_mental_health_specialist,
    find_nearby_therapists_by_location
]


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    api_key=GROQ_API_KEY
)


graph = create_react_agent(
    llm,
    tools=tools
)


SYSTEM_PROMPT = """
You are Dr. Aaditya, an empathetic AI mental health therapist and counselor.

When someone asks who you are, clearly identify yourself as Dr. Aaditya.

Available tools:

1. ask_mental_health_specialist
2. find_nearby_therapists_by_location

Rules:

- Use ask_mental_health_specialist for emotional support.
- Use find_nearby_therapists_by_location if user requests nearby therapists.

Always be warm, supportive, and professional.
"""


def parse_response(stream):

    tool_called_name = "None"
    final_response = None

    for s in stream:

        tool_data = s.get("tools")

        if tool_data:

            tool_messages = tool_data.get("messages")

            if tool_messages:

                for msg in tool_messages:

                    tool_called_name = getattr(
                        msg,
                        "name",
                        "None"
                    )

        agent_data = s.get("agent")

        if agent_data:

            messages = agent_data.get("messages")

            if messages:

                for msg in messages:

                    if msg.content:

                        final_response = msg.content

    return tool_called_name, final_response
