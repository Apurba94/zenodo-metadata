"""Zenodo legacy deposit metadata (.zenodo.json, used by the GitHub integration)."""
import datetime
import re

UPLOAD_TYPES = ("publication", "poster", "presentation", "dataset", "image", "video", "software", "lesson",
                "physicalobject", "other")
PUBLICATION_TYPES = ("annotationcollection", "book", "section", "conferencepaper", "datamanagementplan", "article",
                     "patent", "preprint", "deliverable", "milestone", "proposal", "report", "softwaredocumentation",
                     "taxonomictreatment", "technicalnote", "thesis", "workingpaper", "other")
ACCESS = ("open", "embargoed", "restricted", "closed")
RELATIONS = ("isCitedBy", "cites", "isSupplementTo", "isSupplementedBy", "isContinuedBy", "continues", "isDescribedBy",
             "describes", "hasMetadata", "isMetadataFor", "isNewVersionOf", "isPreviousVersionOf", "isPartOf", "hasPart",
             "isReferencedBy", "references", "isDocumentedBy", "documents", "isCompiledBy", "compiles", "isVariantFormOf",
             "isOriginalFormof", "isIdenticalTo", "isAlternateIdentifier", "isReviewedBy", "reviews", "isDerivedFrom",
             "isSourceOf", "requires", "isRequiredBy", "isObsoletedBy", "obsoletes")
_ORCID = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


def _creator(c):
    if isinstance(c, str):
        given, _, family = c.rpartition(" ")
        c = {"name": "%s, %s" % (family, given) if given else family}
    out = {"name": c["name"]}
    for k in ("affiliation", "orcid"):
        if c.get(k):
            out[k] = c[k].rsplit("/", 1)[-1] if k == "orcid" else c[k]
    return out


def build(title, creators, description, upload_type="software", version=None, license="MIT", keywords=(),
          access_right="open", publication_date=None, related=(), communities=(), grants=(), notes=None,
          publication_type=None, language="eng"):
    """related: list of (relation, identifier) such as ('isSupplementTo', '10.1000/xyz')."""
    md = {"title": title, "upload_type": upload_type, "description": description,
          "creators": [_creator(c) for c in creators], "access_right": access_right, "license": license,
          "language": language}
    if upload_type == "publication":
        md["publication_type"] = publication_type or "article"
    if version:
        md["version"] = version
    if keywords:
        md["keywords"] = list(keywords)
    if publication_date:
        md["publication_date"] = publication_date
    if related:
        md["related_identifiers"] = [{"relation": r, "identifier": i, "scheme": "doi" if i.startswith("10.") else "url"}
                                     for r, i in related]
    if communities:
        md["communities"] = [{"identifier": c} for c in communities]
    if grants:
        md["grants"] = [{"id": g} for g in grants]
    if notes:
        md["notes"] = notes
    return md


def validate(md):
    errors, warnings = [], []
    for req in ("title", "upload_type", "description", "creators"):
        if not md.get(req):
            errors.append("missing required field '%s'" % req)
    if md.get("upload_type") and md["upload_type"] not in UPLOAD_TYPES:
        errors.append("upload_type must be one of: " + ", ".join(UPLOAD_TYPES))
    if md.get("upload_type") == "publication" and md.get("publication_type") not in PUBLICATION_TYPES:
        errors.append("publication uploads need a valid publication_type")
    for i, c in enumerate(md.get("creators") or [], 1):
        if not c.get("name"):
            errors.append("creator %d has no name" % i)
        elif "," not in c["name"]:
            warnings.append("creator %d name should be 'Family, Given'" % i)
        if c.get("orcid") and not _ORCID.match(c["orcid"]):
            errors.append("creator %d ORCID must look like 0000-0000-0000-0000" % i)
        if not c.get("affiliation"):
            warnings.append("creator %d has no affiliation" % i)
    if md.get("access_right") and md["access_right"] not in ACCESS:
        errors.append("access_right must be one of: " + ", ".join(ACCESS))
    if md.get("access_right") == "embargoed" and not md.get("embargo_date"):
        errors.append("embargoed records need an embargo_date")
    if md.get("access_right") in ("open", "embargoed") and not md.get("license"):
        errors.append("open/embargoed records need a license")
    if md.get("publication_date"):
        try:
            datetime.date.fromisoformat(md["publication_date"])
        except ValueError:
            errors.append("publication_date must be YYYY-MM-DD")
    for r in md.get("related_identifiers", []):
        if r.get("relation") not in RELATIONS:
            errors.append("unknown relation '%s'" % r.get("relation"))
    if len(md.get("description", "")) < 50:
        warnings.append("description is very short; it is the landing-page abstract")
    if not md.get("keywords"):
        warnings.append("add keywords to improve discoverability")
    if md.get("upload_type") == "software" and not md.get("version"):
        warnings.append("software records should have a version")
    return errors, warnings


def from_cff_dict(cff):
    """Map a parsed CITATION.cff (dict) to Zenodo metadata."""
    creators = []
    for a in cff.get("authors", []):
        name = a.get("name") or "%s, %s" % (a.get("family-names", ""), a.get("given-names", ""))
        creators.append({"name": name.strip(", "), "affiliation": a.get("affiliation", ""), "orcid": a.get("orcid", "")})
    return build(cff.get("title", ""), creators, cff.get("abstract") or cff.get("message", ""),
                 "dataset" if cff.get("type") == "dataset" else "software", cff.get("version"),
                 cff.get("license", "MIT"), cff.get("keywords", ()), publication_date=cff.get("date-released"))
