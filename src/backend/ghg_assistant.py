# class ghg_assistant #
# atributes: model parameteres (model, temperature, max completition tokens, system_config)
# methods:
# - generates response (user_prompt, context)
# - evaluate user prompt (if the question has any relation to the topic)
# - is a valid question (evaluate whether the question is related to GHG topic) TBD
from os import getenv
from groq import Client
from spacy import load
from spacy.matcher import PhraseMatcher

class GHGAssistant():
    
    def __init__(
        self,
        model : str = 'llama-3.3-70b-versatile',
        temperature : float = 0.5,
        max_completion_tokens : int = 800,
    ):
        self.model, self.temp, self.max_tokens = model, temperature, max_completion_tokens
        self.disclaimer = (
            "\n\n**Disclaimer:** Be mindful that this is an AI assistant. "
            "Please consult with a professional before proceeding."
        )
        self.system_config = """You are a digital consultant specializing in Australia's evolving greenhouse gas (GHG) emission regulations. 
        Your task is to help companies navigate the complexities of compliance, accurate emission calculations, and industry-specific scope definitions. 
        Ensure the response is practical, actionable, and aligned with the most recent regulatory updates. 
        If the answer is not available or unclear, state that you do not know.
        """
        # configuration of the system role
        self.conversation = [{
                'role' : 'system',
                'content' : self.system_config
            }]
        # define legal entities for detection of delicate enquiries
        self.legal_entities = ["LAW", "NORP", "ORG", "GPE"]
        self.financial_entities = ["MONEY", "ORG", "PERCENT", "CARDINAL", "PRODUCT"]
        # Define additional legal and financial keywords
        self.legal_terms = ["lawsuit", "attorney", "plaintiff", "defendant", "malpractice", "contract", "liability", "sue", "court", "judge", "compliance", "regulation", "policy", "statute"]
        self.financial_terms = ["investment", "stocks", "bond", "revenue", "profit", "bankruptcy", "tax", "audit", "loan", "mortgage"]
    def is_legal_or_financial(
        self,
        sample_text : str
    ) -> bool:
        """
        takes any text and detects if the text is related to finance or law using a pretrained model
        this might generate issues if the model is not downloaded
        """
        nlp = load("en_core_web_md")
        doc = nlp(sample_text)
        
        matcher = PhraseMatcher(
            vocab = nlp.vocab,
            attr = 'lower'
        )
        # add terms to the matcher
        pattern = [nlp(term) for term in self.legal_terms + self.financial_terms]
        matcher.add('legal_or_financial', pattern)
        flag = False
        for ent in doc.ents:
            if ent.label_ in self.legal_entities or ent.label_ in self.financial_entities:
                flag = True
        matches = matcher(doc)
        if matches:
            flag = True
        return flag
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
                'content' : f"\n\nUse the following context to provide tailored, concise, and accurate guidance.'{context}'"
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
        # check if the content el related to legal or financial terms
        if self.is_legal_or_financial(user_prompt):
            ai_ouput += self.disclaimer
        # add to the existing memory of the conversation
        self.conversation.append(
            {
                'role' : 'assistant',
                'content' : ai_ouput
            }
        )
        return ai_ouput