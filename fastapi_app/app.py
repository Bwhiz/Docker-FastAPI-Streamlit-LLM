from model import chat_bot
import os, time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
import groq
from dotenv import load_dotenv
load_dotenv()

# initialize your Applizations
app = FastAPI()
chat_bot = chat_bot()

# Set GRO_API_KEY = "your api key" in the .env file, then load it below
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = groq.Groq(api_key=GROQ_API_KEY)

@app.route("/chat_batch", methods=["POST"])
async def chat_batch(request: Request):
    try:
        user_input = await request.json()
        
        # Get message
        user_message = user_input.get("message")
        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        # Parse temperature
        try:
            temperature = float(user_input.get("temperature"))
        except ValueError:
            return {"error": "Invalid input, pass a number between 0 and 2."}
        
        # Select model
        selected_model = user_input.get("model")
        if selected_model not in chat_bot.models:
            return {"error": "You did not pass a correct model code!"}
        
        # Generate response
        response = chat_bot.get_response_batch(
            message=user_message, 
            temperature=temperature, 
            model=selected_model
        )
        answer = response.choices[0].message.content
        print(answer)
        
        return PlainTextResponse(content=answer, status_code=200)
    
    except Exception as e:
        return {"error": str(e)}


@app.route("/chat_stream", methods=["POST"])
async def chat_stream(request: Request):
    try:
        user_input = await request.json()
        # get message
        user_message = user_input.get("message")
        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        # When we add temprature
        try:
            temperature = float(user_input.get("temperature"))
        except:
            return {
                "error": "Invalid input, pass a number between 0 and 2."
            }
            
        # # When we add token class
        # try:
        #     selected_token_class = user_input.get("max_tokens")
        #     max_tokens = chat_bot.token_class[selected_token_class]
            
        # except Exception as e:
        #     print("Error with selecting tokens \n", e)
            
        try:
            # When we add model selection
            selected_model  = user_input.get("model")
            if selected_model not in chat_bot.models:
                return {
                    "error": "You did not pass a correct model code!/model not available"
                }
            else:
                model = selected_model
        except Exception as e:
            print("Invalid model input", e)
        # Generate a response adapt appropriately
        response = chat_bot.get_response(message= user_message, temperature=temperature, model=model)
        
        # Stream Response
        def stream_response():
            output = ""
            for message in response:
                token = message.choices[0].delta.content
                if token:
                    # print(token, end="")
                    output += token
                    yield f"""{token}"""
                    # Add a delay between chunks to reduce stream speed
                    time.sleep(0.05)  # Adjust the delay as needed

        return StreamingResponse(stream_response(), media_type="text/plain")
        
    except Exception as e:
        return {"error": str(e)}

# $ uvicorn app:app --host 127.0.0.1 --port 5000