from decouple import config
from openai import OpenAI
import openai

def chatGPTtest(question, prompt):

    client = openai.OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ]
    )

    restext = completion.choices[0].message.content

    return(restext)