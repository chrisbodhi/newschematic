### README

[ ![Codeship Status for chrisbodhi/newschematic](https://app.codeship.com/projects/1569e100-09bc-0136-4c2f-52fbe28f0cfd/status?branch=master)](https://app.codeship.com/projects/281510)

Just my website stuff, now with source control!

[New Schematic](http://newschematic.org)

### Development

Built with Hugo!

- Add a new blog post: `hugo new blog/POST-TITLE.md`
- Add a new project page: `hugo new project/PROJECT.md`
- Add a new talk: `hugo new talk/TALK-TITLE.md`
- Add the Goa theme, from the project root: `md themes && cd $_ && git clone https://github.com/shenoybr/hugo-goa`
- Run the server locally, using the Goa theme: `hugo server --theme=hugo-goa`
- Generate the latest HTML files from the Markdown files, using the Goa theme: `hugo --theme=hugo-goa`

### Deployment

- `./deploy.sh` to generate and deploy the latest content

