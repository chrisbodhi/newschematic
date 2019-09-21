### README

[ ![Codeship Status for chrisbodhi/newschematic](https://app.codeship.com/projects/1569e100-09bc-0136-4c2f-52fbe28f0cfd/status?branch=master)](https://app.codeship.com/projects/281510)

Just my website stuff, now with source control!

[New Schematic](http://newschematic.org)

### Development

Built with Hugo!

- Add a new blog post: `hugo new blog/POST-TITLE.md`
- Add a new project page: `hugo new projects/PROJECT.md`
- Add a new talk: `hugo new talks/TALK-TITLE.md`
- Add the Goa theme, from the project root: `md themes && cd $_ && git clone https://github.com/chrisbodhi/hugo-goa`
- Run the server locally, using the Goa theme: `hugo server --theme=hugo-goa`
- Generate the latest HTML files from the Markdown files, using the Goa theme: `hugo --theme=hugo-goa`

#### With Docker

- Run `docker run --rm -it -v $(pwd):/src -p 1313:1313 klakegg/hugo:0.58.3-alpine server` for serving built files
- Run `docker run --rm -it -v $(pwd):/src -v $(pwd)/output:/target klakegg/hugo:0.58.3-alpine` to build

### Deployment

- Typically: push changes to `master`, watch Codeship ship it; configuration steps on Codeship
- Manually: `./deploy.sh` to generate and deploy the latest content
