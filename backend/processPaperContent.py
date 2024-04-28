import arxiv
import json

# Construct the default API client.
client = arxiv.Client()

# Search for the 10 most recent articles matching the keyword "quantum."
search = arxiv.Search(
  query = "%28ti:stock%29 OR %28ti:stock AND ti:price%29 OR %28ti:stock AND ti:market%29 OR %28ti:stock AND ti:prediction%29 OR %28ti:stock AND ti:trend%29 OR %28ti:stock AND ti:forecasting%29",
  max_results = 1000,
  sort_by = arxiv.SortCriterion.SubmittedDate
)

results = client.results(search)
doc_index = 1

documentList = []
# `results` is a generator; you can iterate over its elements one by one...
for r in results:
  document = {
    'index': doc_index,
    'title': r.title,
    'abstract': r.summary.replace('\n', ' '),
    'link': str(r.links[0])
  }
  documentList.append(document)
  doc_index += 1
  print("done: ", doc_index)

# Writing to sample.json
with open("stockDataset.json", "w") as outfile:
    json.dump(documentList, outfile)