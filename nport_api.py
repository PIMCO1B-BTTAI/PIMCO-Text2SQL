from sec_api import FormNportApi
import pandas as pd

api_key = "b5e8d7370398c6f98007335c3ef3ce6e6ef778ed8d553c537b91d23a073253f1"
endpoint = "https://api.sec-api.io/form-nport"

nportApi = FormNportApi(api_key)

query = {
  "query": "fundInfo.totAssets:[100000000 TO *]",
  "from": "0",
  "size": "10",
  "sort": [{"filedAt": {"order": "desc"}}],
}

response = nportApi.get_data(query)

#print(response["filings"][0])

df = pd.json_normalize(response["filings"])

print(df.shape)
print(df.iloc[1, 1])