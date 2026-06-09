import google.generativeai as genai

api_key=os.getenv("GEMINI_API_KEY")

print("KEY =", API_KEY)

genai.configure(
    api_key=API_KEY
)

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content(
    "Say hello"
)

print(response.text)