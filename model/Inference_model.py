from openai import OpenAI
client = OpenAI()

email_message = """
fdsafasdfasdf
"""

completion = client.chat.completions.create(
  model="ft:gpt-3.5-turbo-0125:personal:uottawahack3:8yWNYh5I",
  messages=[
    {"role": "system", "content": """
     Given the input email and the reponse determine if the email provided below is safe or potentially malicious based on its
content. If the email seems legitimate and does not contain any
harmful intent, threats, or suspicious requests, classify it as
"safe". If the email contains elements typical of phishing attempts,
such as requests for sensitive information, suspicious links, or unusual
sender addresses, classify it as "potentially malicious".
     """},
    {"role": "user", "content": 
     email_message} # Write you prompt in here
  ]
)
print(completion.choices[0].message)