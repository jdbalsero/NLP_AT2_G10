# class ghg_assistant
# atributes: model parameteres (model, temperature, max completition tokens, system_config)
# methods:
# - generates response (user_prompt, context)
# - evaluate user prompt (if the question has any relation to the topic)
# - is a valid question (evaluate whether the question is related to GHG topic) TBD
from os import getenv
from json import loads
from json import JSONDecodeError
from groq import Client

class GHGAssistant():
    def __init__(
        self,
        model : str = 'llama-3.3-70b-versatile',
        temperature : float = 0.5,
        max_completion_tokens : int = 600,
    ):
        self.model, self.temp, self.max_tokens = model, temperature, max_completion_tokens
        self.system_config = """You are a digital consultant specializing in Australia's evolving greenhouse gas (GHG) emission regulations. 
        Your task is to help companies navigate the complexities of compliance, accurate emission calculations, and industry-specific scope definitions. 
        Ensure the response is practical, actionable, and aligned with the most recent regulatory updates. 
        If the answer is not available or unclear, state that you do not know.
        You must return a JSON object following this structure:
        {"response" : <your response to my question> , "category" : <your classification of the user prompt from the following list: ['legal', 'financial', 'others']>}
        """
        self.disclaimer = (
            "\n\n**Disclaimer:** Be mindful that this is an AI assistant. "
            "Please consult with a professional before proceeding."
        )
        # role of the agent (?)
        self.conversation = [{
                'role' : 'system',
                'content' : self.system_config
            }] # configuration of the system role
    def generate_response(
        self,
        user_prompt : str,
        context : str = None
    ):
        client = Client(
            api_key = getenv('GROQ_API_KEY')
        )
        # initialize the conversation
        self.conversation.append(
            # configuration of the response
            {
                'role' : 'assistant',
                'content' : f"\n\nUse the following context to provide tailored, concise, and accurate guidance. '{context}'"
            }
        )
        self.conversation.append(
            # adding the query from the user
            {
                'role' : 'user',
                'content' : user_prompt
            }
        )
        # generating the response
        response = client.chat.completions.create(
            messages = self.conversation,
            model = self.model,
            temperature = self.temp,
            max_completion_tokens = self.max_tokens
        )
        # retreiving the output
        ai_ouput = response.choices[0].message.content
        # this section is based on the assumption that the system config asks for a json file
        try:
            json_format_ai_output = loads(ai_ouput)
            answer = json_format_ai_output.get("response", 'It was not possible to process that prompt')
            category = json_format_ai_output.get("category", 'general')
        except JSONDecodeError: # if the model output cannot be converted into
            print(JSONDecodeError)
            print(ai_ouput)
            answer, category = ai_ouput, 'general'
        # in case the user asks for a sensitive topic
        if category in ['legal', 'financial']:
            answer += self.disclaimer
        # update conversation
        self.conversation.append(
            {
                'role' : 'assistant',
                'content' : answer
            }
        )
        return answer