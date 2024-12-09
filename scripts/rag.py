import chromadb
import os
import pandas as pd
from mdutils.mdutils import MdUtils
from hexagram_generator import (
    get_lines_details,
    retrieve_information,
    format_gua_info,
    hexagram_attrs,
    get_alter_list,
)

df = pd.read_csv("../data/examples/RAG_db.csv", sep="\t")
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
    keep_cols = [
        "id",
        "Q",
        "A",
        "Primary_id",
        "Alter_id",
        "Interp",
        "Day_Stem",
        "Day_Branch",
        "Month_Branch",
    ]
    result = result[keep_cols]
    return result.to_dict(orient="records")


def aggregate_info(examples):
    res = []
    for entry in examples:
        day_stem = entry["Day_Stem"]
        day_branch = entry["Day_Branch"]
        month_branch = entry["Month_Branch"]
        primary_id = str(entry["Primary_id"])
        alter_id = str(entry["Alter_id"])

        primary_details = get_lines_details(
            primary_id, day_stem, day_branch, month_branch
        )
        alter_details = get_lines_details(
            alter_id, day_stem, day_branch, month_branch, primary_id
        )

        diff_lines = get_alter_list(primary_id, alter_id)

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
        res.new_line()

    return res.get_md_text()


def retrieve(query, topk=3):
    examples = search(query, topk)
    res = aggregate_info(examples)
    md_text = format_examples(res)
    return md_text


if __name__ == "__main__":
    print(retrieve("love", 3))
