# sparkins01.github.io

Academic CV website for Professor Simon Parkinson, built with [Jekyll](https://jekyllrb.com/) and hosted on GitHub Pages.

## Pages

| Page | File | Content comes from |
|------|------|--------------------|
| About | `index.html` | Text in the page + `_config.yml` (name, position, links) |
| Publications | `publications.html` | `_data/publications.yml` (generated, see below) |
| Grants | `grants.html` | `_data/grants.yml` |
| Awards | `awards.html` | `_data/awards.yml` |
| Supervision | `supervision.html` | `_data/supervision.yml` |
| Media | `media.html` | `_data/media.yml` |

Most updates are a matter of editing a YAML file in `_data/` and committing; GitHub Pages rebuilds the site automatically.

## Updating publications from Pure

1. Export your research outputs from Pure as BibTeX.
2. Save it as `scripts/pure_export.bib` (this file is git-ignored because the raw export contains internal Pure notes).
3. Run `python3 scripts/bib2yaml.py` (needs `pip install pyyaml`).
4. Commit the changed `_data/publications.yml` and `files/publications.bib`.

The script drops Pure's internal `note` fields from the public BibTeX download.
Publications that are on your CV but not in Pure live in `scripts/extra_publications.yml`
and are merged in automatically. Paper awards and type corrections (e.g. reports that Pure
exports as books) are set near the top of `scripts/bib2yaml.py`.

## Adding a photo or profile links

Put a photo at `assets/img/profile.jpg` and uncomment the `photo:` line in `_config.yml`.
Uncomment and fill in `google_scholar`, `orcid`, `linkedin`, `dblp` or `pure` to add buttons to the About page.

## Previewing locally

```sh
gem install jekyll
jekyll serve
```

Then open http://localhost:4000.
