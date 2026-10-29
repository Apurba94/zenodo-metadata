# zenodo-metadata

**Get a DOI for your code or data with complete, correct metadata: create and validate the
`.zenodo.json` file that Zenodo's GitHub integration reads on every release.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Connecting a GitHub repository to Zenodo archives every release and mints a DOI, making software
citable and preserving it independently of GitHub. Without `.zenodo.json`, Zenodo guesses the
metadata (often wrong authors, no ORCIDs, no affiliations, no link to the paper). With it, every
release is properly attributed and linked.

## Features

- Builds `.zenodo.json` with creators (`Family, Given`, ORCID, affiliation), description, upload type,
  version, licence, keywords, related identifiers (e.g. `isSupplementTo` the paper DOI), communities, grants
- Validates required fields, upload/publication types, ORCID format, access rights (embargo date,
  licence), dates and relation types; warns about missing affiliations, keywords or version
- Converts from CITATION.cff fields (`from_cff_dict`)

## Usage

```bash
pip install .
zenodo-metadata new "Research Automation Toolkit" -c "Lovelace, Ada;0000-0002-1825-0097;University X" \
    -d "Tools that automate daily research work." --version 1.0.0 -k automation -k reproducibility \
    --related isSupplementTo=10.1234/paper.doi
zenodo-metadata validate .zenodo.json
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
