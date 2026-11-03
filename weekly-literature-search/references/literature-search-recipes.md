# Literature search query recipes

No-API-key queries for the weekly literature search. Run each with curl through the terminal tool.

## PubMed (no key)

ESearch (JSON, top N):
```sh
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=60&sort=pub+date&term=(<TERMS>)+AND+pub_date%5BDate%5D%3A<YYYY>%2F<MM>%2F<DD>+TO+<YYYY>%2F<MM>%2F<DD>"
```

Replace <TERMS> with the topical OR-group, e.g.:
```
(spatial+demography+OR+"bayesian+spatial+epidemiology"+OR+"bayesian+demography")
```

Then fetch abstracts for the returned IDs with Efetch:
```sh
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=<comma-separated-IDs>&rettype=abstract&retmode=text"
```

Note: pub_date range filters are sometimes not honored by this endpoint (returns 0 for range queries). If a range query returns 0, fetch abstracts by rank and read the dates from the text.

## Crossref (no key)

```sh
curl -s "https://api.crossref.org/works?query.bibliographic=(<query>)&filter=from-pub-date:<YYYY-MM-DD>,until-pub-date:<YYYY-MM-DD>&rows=25&sort=issued&order=desc"
```

Do not use to-pub-date - it is rejected; use until-pub-date.

## arXiv (no key)

```sh
curl -s "https://export.arxiv.org/api/query?search_query=<QUERY>&max_results=30&sortBy=submittedDate&sortOrder=descending"
```

## Verify a DOI

```sh
curl -sI https://doi.org/<DOI>   # expect HTTP 200, 301, or 302
```
