from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Import the ChatOpenAI class from the langchain_openai module
from langchain_openai import ChatOpenAI


# Create an instance of the ChatOpenAI class
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

# Define the JSON schema for the structured output
laptop_description_schema = {
    "title": "description",
    "description": "get all laptop details including suitability for different user groups.",
    "type": "object",
    "properties": {
        "ram": {"type": "string"},
        "gpu": {"type": "string"},
        "processor": {"type": "string"},
        "storage": {"type": "string"},
        "good_for_students": {
            "type": "object",
            "properties": {
                "is_suitable": {"type": "boolean"},
                "reason": {"type": "string", "description": "Reason why it is suitable or not for students."}
            }
        },
        "good_for_developers": {
            "type": "object",
            "properties": {
                "is_suitable": {"type": "boolean"},
                "reason": {"type": "string", "description": "Reason why it is suitable or not for developers."}
            }
        },
        "good_for_video_editors": {
            "type": "object",
            "properties": {
                "is_suitable": {"type": "boolean"},
                "reason": {"type": "string", "description": "Reason why it is suitable or not for editors."}
            }
        },
        "good_for_gaming": {
            "type": "object",
            "properties": {
                "is_suitable": {"type": "boolean"},
                "reason": {"type": "string", "description": "Reason why it is suitable or not for gaming."}
            }
        },
        "good_for_business": {
            "type": "object",
            "properties": {
                "is_suitable": {"type": "boolean"},
                "reason": {"type": "string", "description": "Reason why it is suitable or not for business Persons."}
            }
        },
        "additional_info": {"type": "string"}
    },
    "required": ["ram", "gpu", "processor", "storage", "good_for_students", "good_for_developers", "good_for_video_editors", "good_for_gaming", "good_for_business", "additional_info"]
}

# Set the structured output for the language model
structured_llm = llm.with_structured_output(laptop_description_schema)

# Define the extraction function
def extractDescriptionAi(content):
    # Invoke the language model with the structured output
    response = structured_llm.invoke(content)
    # Return the response as a dictionary
    return response