import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def elasticsearch_connect():
    host = 'search-dog-finder-v2-7wjebliu7bqocjgom3d6csaxde.us-east-1.es.amazonaws.com'
    service = 'es'
    region = 'us-east-1'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                       region, service, session_token=credentials.token)

    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return es


def search_knn(es: Elasticsearch, prediction: list):
    results = es.search(index='found', body={
        "size": 5,
        "query": {
            "knn": {
                "image-vector": {
                    "vector": prediction,
                    "k": 5
                }
            }
        },
        "_source": ["image-url", "user-id", "entry-id"],
    })
    return results


def get_lost_object(es: Elasticsearch, imageLink: str, entryId: str):
    doc_id = f"{entryId}-{imageLink}"
    results = es.get(index='lost', id=doc_id)
    return results
