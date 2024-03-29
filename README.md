### README

Just my website stuff, now with source control!

[New Schematic](http://newschematic.org)

[![.github/workflows/deploy.yml](https://github.com/chrisbodhi/newschematic/actions/workflows/deploy.yml/badge.svg)](https://github.com/chrisbodhi/newschematic/actions/workflows/deploy.yml)

### Development

Built with Hugo!

- Add a new blog post: `hugo new blog/POST-TITLE.md`
- Add a new project page: `hugo new projects/PROJECT.md`
- Add a new talk: `hugo new talks/TALK-TITLE.md`
- Add the Goa theme, from the project root: `md themes && cd $_ && git clone https://github.com/chrisbodhi/hugo-goa`
    - The theme is copied from `chrisbodhi/hugo-goa` during deploy
- Run the server locally, using the Goa theme: `hugo server --theme=hugo-goa`
- Generate the latest HTML files from the Markdown files, using the Goa theme: `hugo --theme=hugo-goa`

#### With Docker

- Run `docker run --rm -it -v $(pwd):/src -p 1313:1313 klakegg/hugo:0.79.0-alpine server` for serving built files
- Run `docker run --rm -it -v $(pwd):/src -v $(pwd)/output:/target klakegg/hugo:0.79.0-alpine` to build

### Deployment

- Typically: push changes to `master`, watch GitHub Actions ship it; configuration steps in .github/workflow
- Manually: `./deploy.sh` to generate and deploy the latest content
