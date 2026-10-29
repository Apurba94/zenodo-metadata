import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from zenodo_metadata.cli import main
from zenodo_metadata.core import build, from_cff_dict, validate

DESC = "A toolkit of small, tested utilities that automate everyday research tasks for reproducibility."


class BuildTests(unittest.TestCase):
    def test_build_valid_software(self):
        md = build("Toolkit", [{"name": "Lovelace, Ada", "orcid": "https://orcid.org/0000-0002-1825-0097",
                                "affiliation": "Uni"}], DESC, version="1.0.0", keywords=["automation"],
                   related=[("isSupplementTo", "10.1000/paper"), ("isDocumentedBy", "https://docs.example.org")])
        self.assertEqual(md["creators"][0]["orcid"], "0000-0002-1825-0097")
        self.assertEqual(md["related_identifiers"][1]["scheme"], "url")
        self.assertEqual(validate(md), ([], []))

    def test_string_creator_and_publication_type(self):
        md = build("Paper", ["Ada Lovelace"], DESC, upload_type="publication")
        self.assertEqual(md["creators"][0]["name"], "Lovelace, Ada")
        self.assertEqual(md["publication_type"], "article")

    def test_validation_errors(self):
        md = {"title": "x", "upload_type": "code", "description": "short", "access_right": "embargoed",
              "creators": [{"name": "Ada", "orcid": "123"}], "publication_date": "2026/01/01",
              "related_identifiers": [{"relation": "likes", "identifier": "x"}]}
        errors, warnings = validate(md)
        text = " ".join(errors)
        for frag in ("upload_type", "ORCID", "embargo_date", "license", "YYYY-MM-DD", "unknown relation"):
            self.assertIn(frag, text)
        self.assertTrue(any("Family, Given" in w for w in warnings))

    def test_from_cff(self):
        cff = {"title": "T", "type": "software", "version": "2.0", "license": "Apache-2.0", "date-released": "2026-02-02",
               "authors": [{"family-names": "Lovelace", "given-names": "Ada", "orcid": "https://orcid.org/0000-0002-1825-0097"}],
               "abstract": DESC, "keywords": ["k"]}
        md = from_cff_dict(cff)
        self.assertEqual(md["creators"][0], {"name": "Lovelace, Ada", "orcid": "0000-0002-1825-0097"})
        self.assertEqual((md["version"], md["license"], md["publication_date"]), ("2.0", "Apache-2.0", "2026-02-02"))

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, ".zenodo.json")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = main(["new", "Toolkit", "-c", "Lovelace, Ada;0000-0002-1825-0097;Uni", "-d", DESC,
                             "--version", "1.0", "-k", "research", "--related", "isSupplementTo=10.1/x", "-o", out])
                self.assertEqual(code, 0)
                self.assertEqual(main(["validate", out]), 0)
            with open(out, encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["related_identifiers"][0]["relation"], "isSupplementTo")


if __name__ == "__main__":
    unittest.main()
