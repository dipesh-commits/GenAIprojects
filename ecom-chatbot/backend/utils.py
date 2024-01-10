import os
import pandas as pd
import openai
import tiktoken
import numpy as np
import csv

from langchain import agents
from langchain.document_loaders import CSVLoader, TextLoader

from dotenv import load_dotenv

load_dotenv()


def create_embeddings():
    domain = "saatva.com"

    openai_api_key = os.getenv('OPENAI_API_KEY')
    print(openai_api_key)

    if not os.path.exists("processed"):
        os.mkdir("processed")

    def remove_newlines(serie):
        serie = serie.str.replace("\n", " ")
        serie = serie.str.replace("  ", " ")
        serie = serie.str.replace("  ", " ")
        return serie
    
    
    def document_loader():
        return CSVLoader("processed/scraped.csv")
    

    texts = []

    for file in os.listdir("../scraper/data/www." + domain + "/"):
        with open(
            "../scraper/data/www." + domain + "/" + file, "r", encoding="UTF-8", errors='replace'
        ) as f:
            text = f.read()

            # Omit the first 11 lines and the last 4 lines, then replace -, _, and #update with spaces.
            texts.append(
                (
                    file[11:-4]
                    .replace("-", " ")
                    .replace("_", " ")
                    .replace("#update", ""),
                    text,
                )
            )

    df = pd.DataFrame(texts, columns=["fname", "text"])

    df["text"] = df.fname + ". " + remove_newlines(df.text)
    df.to_csv("processed/scraped.csv", escapechar="\\", quoting=csv.QUOTE_ALL)

    tokenizer = tiktoken.get_encoding("cl100k_base")

    df = pd.read_csv("processed/scraped.csv", index_col=0)
    df.columns = ["title", "text"]

    df["n_tokens"] = df.text.apply(lambda x: len(tokenizer.encode(x)))

    max_tokens = 2000

    # Split the text into chunks of a maximum number of tokens
    def split_into_many(text, max_tokens=max_tokens):
        sentences = text.split(". ")

        n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]

        chunks = []
        tokens_so_far = 0
        chunk = []

        for sentence, token in zip(sentences, n_tokens):
            # If the number of tokens so far plus the number of tokens in the current sentence is greater than the max number of tokens, then add the chunk to the list of chunks and reset the chunk and tokens so far
            if tokens_so_far + token > max_tokens:
                chunks.append(". ".join(chunk) + ".")
                chunk = []
                tokens_so_far = 0

            # If the number of tokens in the current sentence is greater than the max number of tokens, go to the next sentence
            if token > max_tokens:
                continue

            # Otherwise, add the sentence to the chunk and add the number of tokens to the total
            chunk.append(sentence)
            tokens_so_far += token + 1

        # Add the last chunk to the list of chunks
        if chunk:
            chunks.append(". ".join(chunk) + ".")

        return chunks

    shortened = []

    # Loop through the dataframe
    for row in df.iterrows():
        if row[1]["text"] is None:
            continue

        if row[1]["n_tokens"] > max_tokens:
            shortened += split_into_many(row[1]["text"])

        else:
            shortened.append(row[1]["text"])

    df = pd.DataFrame(shortened, columns=["text"])
    df["n_tokens"] = df.text.apply(lambda x: len(tokenizer.encode(x)))
    df.n_tokens.hist()

    df["embeddings"] = df.text.apply(
        lambda x: openai.Embedding.create(input=x, engine="text-embedding-ada-002")[
            "data"
        ][0]["embedding"]
    )
    df.to_csv("processed/embeddings.csv")
    print("Embeddings created successfully..........")


if __name__ == "__main__":
    create_embeddings()
    

    


