import chromadb
import os
import pandas as pd
from mdutils.mdutils import MdUtils
from hexagram_generator import (
    get_lines_details,
    retrieve_information,
    format_gua_info,
    gua_attrs,
)

df = pd.read_csv("../data/example.csv", sep="\t")
df["id"] = df["id"].astype(str)
documents = list(df["Q"])
all_ids = list(df["id"])
client = chromadb.Client()
openai_ef = chromadb.utils.embedding_functions.OpenAIEmbeddingFunction(
    model_name="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY"),
)
collection = client.get_or_create_collection(
    name="iching", embedding_function=openai_ef
)

collection.upsert(ids=all_ids, documents=documents)


def search(query, topk=3) -> pd.DataFrame:
    query_res = collection.query(
        query_texts=[query],
        n_results=topk,
    )
    ids = query_res["ids"][0]
    result = df[df["id"].isin(ids)]
    keep_cols = ["id", "Q", "A", "Primary_id", "Alter_id", "Interp", "Day_Stem"]
    result = result[keep_cols]
    return result.to_dict(orient="records")


def aggregate_info(examples):
    res = []
    for entry in examples:
        t = entry["Day_Stem"]
        primary_id = str(entry["Primary_id"])
        alter_id = str(entry["Alter_id"])

        primary_details = get_lines_details(primary_id, t)
        alter_details = get_lines_details(alter_id, t, primary_id)

        primary_binary = gua_attrs[primary_id]["binary"]
        alter_binary = gua_attrs[alter_id]["binary"]
        diff_lines = [i + 1 for i in range(6) if primary_binary[i] != alter_binary[i]]

        gua_info = retrieve_information(
            primary_id, alter_id, diff_lines, primary_details, alter_details
        )
        entry["gua_info"], _ = format_gua_info(gua_info)
        res.append(entry)
    return res


def format_examples(info):
    res = MdUtils(file_name="")
    for i, entry in enumerate(info):
        res.new_header(level=1, title=f"Example {i+1}")
        res.new_header(level=2, title=f"Question: {entry['Q']}")
        res.file_data_text += entry["gua_info"]
        res.new_header(level=2, title="Hexagram Interpretation")
        res.new_line(entry["Interp"])
        res.new_header(level=2, title="Answer")
        res.new_line(entry["A"])
        res.new_line()

    return res.get_md_text()


def retrieve(query, topk=3):
    examples = search(query, topk)
    res = aggregate_info(examples)
    md_text = format_examples(res)
    return md_text


if __name__ == "__main__":
    print(retrieve("love", 3))
