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

#### With Docker

- Run `docker run --rm -it -v $(pwd):/src -p 1313:1313 klakegg/hugo:0.151.0-ext-alpine server` for serving built files
- Run `docker run --rm -it -v $(pwd):/src -v $(pwd)/output:/target klakegg/hugo:0.151.0-ext-alpine` to build

### Deployment

- Push changes to `master` and GitHub Actions will automatically build and deploy
- The PaperMod theme is automatically fetched during the GitHub Actions workflow
- Configuration steps are in `.github/workflows/`
