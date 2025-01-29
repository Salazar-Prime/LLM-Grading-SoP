"""
OpenAI API utility functions for processing statements of purpose.
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


def initialize_openai_client():
    """
    Initialize and return an OpenAI client.

    Returns:
        OpenAI: Configured OpenAI client
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return client
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        raise


def load_system_prompt(prompt_file="systemPromptv2.txt"):
    """
    Load system prompt from a text file.

    Args:
        prompt_file (str): Path to the system prompt file

    Returns:
        str: System prompt text
    """
    try:
        with open(prompt_file, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"System prompt file {prompt_file} not found.")
        return "You are a helpful assistant."


def getResponse(sop_text, json_schema, model="gpt-4o-mini"):
    """
    Get OpenAI response for a given statement of purpose.

    Args:
        sop_text (str): Statement of purpose text
        json_schema (dict): JSON schema for the response
        model (str, optional): OpenAI model to use. Defaults to "gpt-3.5-turbo".

    Returns:
        dict: Response from OpenAI
    """
    try:
        # Initialize client
        client = initialize_openai_client()

        # Load system prompt
        system_prompt = load_system_prompt()

        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": sop_text},
        ]

        # response format
        response_format = {"type": "json_schema", "json_schema": json_schema}

        # Make API call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format=response_format,
            max_tokens=1000,
            temperature=0.1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Convert usage to a dictionary
        usage_dict = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

        # return reponse as a json object
        response_json = json.loads(response.choices[0].message.content)
        # Extract and return response
        return {
            "response": response_json,
            "usage_log": usage_dict,
        }

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return {"error": str(e)}

    return response.choices[0].message.content
