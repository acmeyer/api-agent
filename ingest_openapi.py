import requests
import yaml
import tiktoken
from openai_service import get_chat_completion
from langchain.schema import Document
from openapi_spec import dereference_openapi_spec, get_spec_endpoints, get_spec_title_and_version, reduce_openapi_spec
from utils import truncate
from vectorstore import upload_docs_to_pinecone


def generate_endpoint_summaries(
    endpoints: list[dict], 
    spec: dict,
    model: str = "gpt-3.5-turbo"
):
    """Creates summaries for OpenAPI endpoints"""
    print("""Summarizing endpoints""")
    assert model in ["gpt-3.5-turbo", "gpt-4"], "Invalid model"
    if model == "gpt-3.5-turbo":
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    elif model == "gpt-4":
        encoding = tiktoken.encoding_for_model("gpt-4")
    else:
        raise ValueError("Invalid model")
    
    title, version = get_spec_title_and_version(spec)
    summary_docs = []
    summaries = []
    summary_prompt = open("prompts/openapi_endpoint_summary.txt").read() + "\n"
    for endpoint in endpoints:
        endpoint_str = str(endpoint)
        prompt = summary_prompt.format(endpoint=truncate(encoding, endpoint_str, 3100))
        summary = get_chat_completion(
            model=model,
            messages=[{
                "role": "user", 
                "content": prompt
            }],
            max_tokens=700
        )
        summaries.append(summary)
        summary_docs.append(Document(
            page_content=summary,
            metadata={
                "endpoint": endpoint[0],
                "api_name": title,
                "api_version": version,
                "api_url": spec.get("servers", [{}])[0].get("url", "")
            }
        ))

    print("Done summarizing docs")
    upload_docs_to_pinecone(summary_docs, "endpoint_summaries")
    return summaries


def generate_overall_api_summary(
    endpoint_summaries: list[str],
    spec: dict,
    model: str = "gpt-3.5-turbo"
):
    """Creates a summary for the overall API"""
    print("""Summarizing overall API""")
    assert model in ["gpt-3.5-turbo", "gpt-4"], "Invalid model"
    if model == "gpt-3.5-turbo":
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    elif model == "gpt-4":
        encoding = tiktoken.encoding_for_model("gpt-4")
    
    summary_prompt = open("prompts/openapi_overall_summary.txt").read() + "\n"
    prompt = summary_prompt.format(endpoint_summaries=truncate(encoding, "\n\n".join(endpoint_summaries), 3100))
    summary = get_chat_completion(
        model=model,
        messages=[{
            "role": "user", 
            "content": prompt
        }],
        max_tokens=700
    )

    title, version = get_spec_title_and_version(spec)
        
    print("Done summarizing API")

    summary_doc = Document(
        page_content=summary,
        metadata={
            "api_name": title,
            "api_version": version,
            "api_url": spec.get("servers", [{}])[0].get("url", "")
        }
    )
    upload_docs_to_pinecone([summary_doc], "api_summaries")
    return summary


def ingest_openapi_file(url) -> dict:
    response = requests.get(url)
    if response.status_code == 200:
        # Figure out if the file is JSON or YAML
        if url.endswith(".json"):
            # Parse the JSON content into a Python dictionary
            raw_api_spec = response.json()
        elif url.endswith(".yaml") or url.endswith(".yml"):
            # Parse the YAML content into a Python dictionary
            content = response.content.decode('utf-8', 'ignore')
            raw_api_spec = yaml.safe_load(content)
        else:
            raise Exception(f"Invalid file type. Must be JSON or YAML. URL: {url}")
        dereferenced_spec = dereference_openapi_spec(raw_api_spec)
        dereferenced_and_reduced_spec = reduce_openapi_spec(dereferenced_spec)
        return dereferenced_and_reduced_spec
    else:
        raise Exception(f"Failed to download the YAML file. Status code: {response.status_code}")


def get_openapi_endpoint_chunks(openapi_spec: dict) -> list[dict]:
    """Generate summaries for each endpoint in an OpenAPI spec."""

    print("Starting chunking out endpoints")
    endpoints = get_spec_endpoints(openapi_spec)
    print("Finished chunking endpoints")

    endpoint_docs = [Document(
        page_content=str(endpoint),
        metadata={
            "endpoint": endpoint[0],
            "api_name": openapi_spec.get("info", {}).get("title", ""),
            "api_version": openapi_spec.get("info", {}).get("version", ""),
            "api_url": openapi_spec.get("servers", [{}])[0].get("url", "")
        }
    ) for endpoint in endpoints]
    upload_docs_to_pinecone(endpoint_docs, "api_endpoints")
    return endpoints

if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-u", "--url", type=str, help="URL to summarize")
    argparser.add_argument("-m", "--model", type=str, help="Model to use", default="gpt-3.5-turbo")
    args = argparser.parse_args()
    url = args.url
    api_url = url
    model = args.model

    openapi_spec = ingest_openapi_file(api_url)
    endpoint_chunks = get_openapi_endpoint_chunks(openapi_spec)
    summaries = generate_endpoint_summaries(endpoint_chunks, spec=openapi_spec, model=model)
    overall_summary = generate_overall_api_summary(summaries, spec=openapi_spec, model=model)