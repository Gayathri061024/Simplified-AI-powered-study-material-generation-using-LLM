import json
from groq import Groq
client = Groq(api_key='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')
models = [m.id for m in client.models.list().data]
print("MODELS:", models)
with open("debug_out.txt", "w") as f:
    f.write(json.dumps(models))
