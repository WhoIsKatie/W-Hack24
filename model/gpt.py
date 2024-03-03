from openai import OpenAI
client = OpenAI()

client.files.create(
  file=open("finetunedata_corrected.jsonl", "rb"),
  purpose="fine-tune"
)