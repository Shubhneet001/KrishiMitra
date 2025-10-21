from langchain_community.vectorstores import FAISS
from langchain.memory import VectorStoreRetrieverMemory, ConversationBufferMemory, CombinedMemory
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import Dict, Union, Tuple
import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class KrishiMitra:
    """Agricultural AI Assistant"""
    
    def __init__(self, default_location: str = "Pune"):
        self.location = default_location
        self._initialize_embeddings()
        self._initialize_llm()
        self._initialize_memory()
        self._initialize_chain()
        self.weather_context = self._get_weather_context() or "<p>Weather data not available.</p>"
    
    def _initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            logger.info("Embeddings initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            raise
    
    def _initialize_llm(self):
        """Initialize language model"""
        try:
            api_token = os.getenv("HUGGINGFACE_API_TOKEN")
            if not api_token:
                raise ValueError("HUGGINGFACE_API_TOKEN not found in environment")
            
            self.llm = HuggingFaceEndpoint(
                repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
                task="text-generation",
                temperature=0.7,
                max_new_tokens=512,
                huggingfacehub_api_token=api_token
            )
            self.model = ChatHuggingFace(llm=self.llm)
            logger.info("LLM initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise
    
    def _initialize_memory(self):
        """Initialize conversation memory"""
        try:
            self.buffer_memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            self.memory_store = FAISS.from_texts(
                ["Initial context"],
                self.embeddings
            )
            
            self.memory_retriever = self.memory_store.as_retriever(
                search_type="mmr",
                search_kwargs={'k': 5, 'fetch_k': 10, 'lambda_mult': 0.7}
            )
            
            self.vector_memory = VectorStoreRetrieverMemory(
                retriever=self.memory_retriever
            )
            
            self.memory = CombinedMemory(
                memories=[self.buffer_memory, self.vector_memory]
            )
            logger.info("Memory initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing memory: {e}")
            raise
    
    def _initialize_chain(self):
        """Initialize the conversation chain"""
        try:
            self.prompt_template = """
You are Krishi Mitra, an advanced AI agricultural assistant specialized in helping farmers.

Return responses in clean, structured HTML format with proper formatting:
- Use <h3>, <h4> for headings
- Use <p> for paragraphs
- Use <ul>, <li> for lists
- Use <strong> for emphasis
- Use <br> for line breaks when needed

Current Weather Information:
{weather_context}

Conversation History (use if relevant):
{history}

User Query: {query}

Provide practical, actionable advice based on the weather conditions and farming best practices.
Your response:
"""
            
            self.prompt = PromptTemplate(
                template=self.prompt_template,
                input_variables=["weather_context", "history", "query"]
            )
            
            self.parser = StrOutputParser()
            self.chain = self._make_chain()
            logger.info("Chain initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing chain: {e}")
            raise
    
    def _make_chain(self):
        """Create the runnable chain"""
        def get_history(query: str):
            try:
                history_vars = self.memory.load_memory_variables({'input': query})
                history = history_vars.get("chat_history", [])
                
                if isinstance(history, list):
                    formatted_history = "\n".join(
                        f"{msg.type.upper()}: {msg.content}" for msg in history
                    )
                else:
                    formatted_history = str(history)
                
                return formatted_history
            except Exception as e:
                logger.error(f"Error getting history: {e}")
                return ""
        
        parallel_chain = RunnableParallel({
            'weather_context': RunnableLambda(lambda _: self.weather_context),
            'history': RunnableLambda(get_history),
            'query': RunnablePassthrough()
        })
        
        return parallel_chain | self.prompt | self.model | self.parser
    
    def get_weather_data(self, location: str = None) -> Dict:
        """Fetch weather data for a location"""
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            logger.warning("Weather API key not found")
            return None
        
        location = location or self.location
        
        try:
            current_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"
            forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=7&aqi=no&alerts=no"
            
            current_response = requests.get(current_url, timeout=10)
            forecast_response = requests.get(forecast_url, timeout=10)
            
            if current_response.status_code == 200 and forecast_response.status_code == 200:
                current_data = current_response.json()
                forecast_data = forecast_response.json()
                
                return {
                    "location": current_data["location"]["name"],
                    "region": current_data["location"]["region"],
                    "country": current_data["location"]["country"],
                    "temperature": current_data["current"]["temp_c"],
                    "feels_like": current_data["current"]["feelslike_c"],
                    "conditions": current_data["current"]["condition"]["text"],
                    "humidity": current_data["current"]["humidity"],
                    "wind_speed": current_data["current"]["wind_kph"],
                    "wind_direction": current_data["current"]["wind_dir"],
                    "rainfall": current_data["current"].get("precip_mm", 0),
                    "cloud_cover": current_data["current"]["cloud"],
                    "uv_index": current_data["current"]["uv"],
                    "forecast": forecast_data["forecast"]["forecastday"]
                }
            else:
                logger.warning(f"Weather API returned status {current_response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in weather data fetch: {e}")
            return None
    
    def _get_weather_context(self) -> str:
        """Format weather data as HTML context"""
        weather_info = self.get_weather_data()
        
        if not weather_info:
            return "<p>Weather data not available.</p>"
        
        return f"""
<div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px;">
    <h4>🌤 Current Weather in {weather_info['location']}, {weather_info['region']}</h4>
    <p><strong>Temperature:</strong> {weather_info['temperature']}°C (Feels like: {weather_info['feels_like']}°C)</p>
    <p><strong>Conditions:</strong> {weather_info['conditions']}</p>
    <p><strong>Humidity:</strong> {weather_info['humidity']}%</p>
    <p><strong>Wind:</strong> {weather_info['wind_speed']} kph {weather_info['wind_direction']}</p>
    <p><strong>Rainfall:</strong> {weather_info['rainfall']} mm</p>
    <p><strong>Cloud Cover:</strong> {weather_info['cloud_cover']}%</p>
    <p><strong>UV Index:</strong> {weather_info['uv_index']}</p>
</div>
"""
    
    def update_location(self, new_location: str):
        """Update the location and refresh weather data"""
        self.location = new_location
        self.weather_context = self._get_weather_context()
        logger.info(f"Location updated to: {new_location}")
    
    def ask(self, query: str) -> str:
        """
        Process a user query and return response
        
        Args:
            query: User's question
            
        Returns:
            HTML formatted response
        """
        try:
            # Invoke the chain
            answer = self.chain.invoke(query)
            
            # Save to memory
            self.buffer_memory.save_context(
                {"input": query},
                {"output": answer}
            )
            
            self.vector_memory.save_context(
                {"input": query},
                {"output": answer, "timestamp": datetime.now(timezone.utc).isoformat()}
            )
            
            return answer
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"<p>Sorry, I encountered an error processing your request: {str(e)}</p>"
    
    def clear_memory(self):
        """Clear conversation memory"""
        try:
            self.buffer_memory.clear()
            logger.info("Memory cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
