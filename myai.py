import generativeai as genai

# Directly set your API key
api_key = "your_api_key_here"

# Initialize the API client with your API key
genai.initialize(api_key=api_key)

# Create a model instance (ensure the class name and method are correct as per documentation)
model = genai.TextModel(model='gemini-1.5-flash')

# Generate content with the model (ensure the method name is correct)
response = model.generate(prompt="Write a story about an AI and magic", max_tokens=150)

# Print the generated text
print(response['text'])
