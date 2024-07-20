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
    "description": "Get all laptop details including suitability for different user groups.",
    "type": "object",
    "properties": {
        "ram": {"type": "string"},
        "gpu": {"type": "string"},
        "processor": {"type": "string"},
        "storage": {"type": "string"},
        "good_for_students": {
            "type": "object",
            "properties": {
                "is_suitable": {
                    "type": "boolean",
                    "description": "Indicates if the laptop is suitable for students. 'true' if the laptop meets students' needs, 'false' if it does not. Suitability can be assessed as good, bad, overkill, or overpriced."
                },
                "reason": {
                    "type": "string",
                    "description": "Detailed explanation of why the laptop is or is not suitable for students. This should include aspects such as performance, features, price relative to students' needs, and any specific reasons why the laptop might be considered good, bad, overkill, or overpriced for student use."
                }
            }
        },
        "good_for_developers": {
            "type": "object",
            "properties": {
                "is_suitable": {
                    "type": "boolean",
                    "description": "Indicates if the laptop is suitable for developers. 'true' if the laptop meets developers' needs, 'false' if it does not. Suitability can be assessed as good, bad, overkill, or overpriced."
                },
                "reason": {
                    "type": "string",
                    "description": "Detailed explanation of why the laptop is or is not suitable for developers. This should include aspects such as performance, features, price relative to developers' needs, and any specific reasons why the laptop might be considered good, bad, overkill, or overpriced for development work."
                }
            }
        },
        "good_for_video_editors": {
            "type": "object",
            "properties": {
                "is_suitable": {
                    "type": "boolean",
                    "description": "Indicates if the laptop is suitable for video editors. 'true' if the laptop meets video editors' needs, 'false' if it does not. Suitability can be assessed as good, bad, overkill, or overpriced."
                },
                "reason": {
                    "type": "string",
                    "description": "Detailed explanation of why the laptop is or is not suitable for video editors. This should include aspects such as processing power, graphics capability, storage, and any specific reasons why the laptop might be considered good, bad, overkill, or overpriced for video editing tasks."
                }
            }
        },
        "good_for_gaming": {
            "type": "object",
            "properties": {
                "is_suitable": {
                    "type": "boolean",
                    "description": "Indicates if the laptop is suitable for gaming. 'true' if the laptop meets gaming needs, 'false' if it does not. Suitability can be assessed as good, bad, overkill, or overpriced."
                },
                "reason": {
                    "type": "string",
                    "description": "Detailed explanation of why the laptop is or is not suitable for gaming. This should include aspects such as graphics performance, processor speed, RAM, and any specific reasons why the laptop might be considered good, bad, overkill, or overpriced for gaming."
                }
            }
        },
        "good_for_business": {
            "type": "object",
            "properties": {
                "is_suitable": {
                    "type": "boolean",
                    "description": "Indicates if the laptop is suitable for business persons. 'true' if the laptop meets business needs, 'false' if it does not. Suitability can be assessed as good, bad, overkill, or overpriced."
                },
                "reason": {
                    "type": "string",
                    "description": "Detailed explanation of why the laptop is or is not suitable for business persons. This should include aspects such as performance, reliability, features relevant to business tasks, and any specific reasons why the laptop might be considered good, bad, overkill, or overpriced for business use."
                }
            }
        },
        "additional_info": {"type": "string"}
    },
    "required": [
        "ram", "gpu", "processor", "storage",
        "good_for_students", "good_for_developers",
        "good_for_video_editors", "good_for_gaming",
        "good_for_business", "additional_info"
    ]
}

# Set the structured output for the language model
structured_llm = llm.with_structured_output(laptop_description_schema)

# Define the extraction function
def extractDescriptionAi(content):
    # Invoke the language model with the structured output
    response = structured_llm.invoke(content)
    # Return the response as a dictionary
    return response