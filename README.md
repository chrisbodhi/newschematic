### README

Just my website stuff, now with source control!

[New Schematic](http://newschematic.org)

[![.github/workflows/deploy.yml](https://github.com/chrisbodhi/newschematic/actions/workflows/deploy.yml/badge.svg)](https://github.com/chrisbodhi/newschematic/actions/workflows/deploy.yml)

### Development

Built with Hugo!

- Add a new blog post: `hugo new blog/POST-TITLE.md`
- Add a new project page: `hugo new projects/PROJECT.md`
- Add a new talk: `hugo new talks/TALK-TITLE.md`
- Run the server locally: `hugo server`
- Generate the latest HTML files from the Markdown files: `hugo --minify`

#### Blyg

The `/blyg/` surfaces come from [hugo-blyg](https://github.com/chrisbodhi/hugo-blyg), a Hugo Module pinned in `go.mod`.

- Stamp a new or edited item: `python3 "$(go list -m -f '{{.Dir}}' github.com/chrisbodhi/hugo-blyg)/scripts/blyg_stamp.py"` (run `go mod download github.com/chrisbodhi/hugo-blyg` once first)
- Upgrade: `hugo mod get github.com/chrisbodhi/hugo-blyg@<tag>`, and set the same tag on the `uses:` line in `.github/workflows/blyg-issue.yml`
- Work on the module against this site: add `replace github.com/chrisbodhi/hugo-blyg => ../hugo-blyg` to `go.mod` (a local checkout), and drop it before committing

#### With Docker

- Run `docker run --rm -it -v $(pwd):/src -p 1313:1313 klakegg/hugo:0.151.0-ext-alpine server` for serving built files
- Run `docker run --rm -it -v $(pwd):/src -v $(pwd)/output:/target klakegg/hugo:0.151.0-ext-alpine` to build

### Deployment

- Push changes to `master` and GitHub Actions will automatically build and deploy
- Configuration steps are in `.github/workflows/`
- File an issue labeled `blyg`, or titled `blyg: …` (e.g. from GitHub Mobile, which can't add labels), (as the repo owner, or a login listed under `authors` in `.github/workflows/blyg-issue.yml`) to publish a blyg fragment: the body becomes the item, the title only names the file and PR. The Action ([`chrisbodhi/hugo-blyg/publish-from-issue`](https://github.com/chrisbodhi/hugo-blyg#the-publish-from-issue-action)) opens a PR; merging it deploys and closes the issue
