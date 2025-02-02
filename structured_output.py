from typing import Type, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
import constants
from typing import TypedDict



# Define the State structure (similar to previous definition)
class State(TypedDict):
    messages: list
    output: Optional[BaseModel]


# Generic Pydantic model-based structured output extractor
class StructuredOutputExtractor:
    def __init__(self, response_schema: Type[BaseModel]):
        """
        Initializes the extractor for any given structured output model.
        
        :param response_schema: Pydantic model class used for structured output extraction
        """
        self.response_schema = response_schema

        # Initialize language model (provider and API keys come from constants.py)
        self.llm = self._choose_llm_provider(constants.CHOSEN_LLM_PROVIDER)
        
        # Bind the model with structured output capability
        self.structured_llm = self.llm.with_structured_output(response_schema)
        
        # Build the graph for structured output
        self._build_graph()

    def _build_graph(self):
        """
        Build the LangGraph computational graph for structured extraction.
        """
        graph_builder = StateGraph(State)

        # Add nodes and edges for structured output
        graph_builder.add_node("extract", self._extract_structured_info)
        graph_builder.add_edge(START, "extract")
        graph_builder.add_edge("extract", END)

        self.graph = graph_builder.compile()

    def _extract_structured_info(self, state: dict):
        """
        Extract structured information using the specified response model.
        
        :param state: Current graph state
        :return: Updated state with structured output
        """
        query = state['messages'][-1].content
        print(f"Processing query: {query}")
        try:
            # Extract details using the structured model
            output = self.structured_llm.invoke(query)
            # Return the structured response
            return {"output": output}
        except Exception as e:
            print(f"Error during extraction: {e}")
            return {"output": None}

    def extract(self, query: str) -> Optional[BaseModel]:
        """
        Public method to extract structured information.
        
        :param query: Input query for structured output extraction
        :return: Structured model object or None
        """
        from langchain_core.messages import HumanMessage

        result = self.graph.invoke({
            "messages": [HumanMessage(content=query)]
        })
        # Return the structured model response, if available
        result = result.get('output')
        return result

    def _choose_llm_provider(self, chosen_llm_provider):
        """Dynamically imports and selects the LLM provider based on configuration, and asks to install the library if it's missing."""
        api_key = constants.llm_api_keys.get(chosen_llm_provider)
        if chosen_llm_provider == 'openai':
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=constants.selected_llm_model.get('openai'), streaming=True, api_key=api_key)
        elif chosen_llm_provider == 'ollama':
            from langchain_ollama import ChatOllama
            return ChatOllama(model=constants.selected_llm_model.get('ollama'))  # streaming is enabled by default
        elif chosen_llm_provider == 'groq':
            from langchain_groq import ChatGroq
            return ChatGroq(model=constants.selected_llm_model.get('groq'), streaming=True, api_key=api_key)
        elif chosen_llm_provider == 'anthropic':
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=constants.selected_llm_model.get('anthropic'), streaming=True, api_key=api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {chosen_llm_provider}")


if __name__ == '__main__':
        
        # Example Pydantic model (e.g., Movie)
        class Movie(BaseModel):
            title: str = Field(description="the title of the youtube video")
            title_image: str = Field(description="highly detailed and descriptive image prompt for the Title")
            items: list[str] = Field(description="top n number of requested items")
            image_prompts: list[str] = Field(description="highly detailed and descriptive image prompts for each item ")



        # Example usage with a generic structured extractor
        extractor = StructuredOutputExtractor(response_schema=Movie)

        query = "Top 5 Superheroes"

        result = extractor.extract(query)
        print(type(result))
        if result:
            print(result)