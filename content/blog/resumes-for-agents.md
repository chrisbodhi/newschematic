+++
title = "Resumes for decks, LinkedIn, and agents"
date = "2026-04-23T14:00:00-05:00"
draft = true
categories = []
tags = []
comments = false
showcomments = false
showpagemeta = true
+++

There's a version of the future where everyone has a deck, instead of a smartphone. The GUI stopped at the TUI and we're all probably smoking cigarettes or doing eye-drugs. Basically what would have turned out if Apple never happened. Resumes would be slung over modems that would be optimized for terminals instead of a PDF viewer that ships in a browser (that also ships four other rendering and computation engines).

In this cyberpunk world, that resume could read like this:

```
      ╔══════════════════════════════════════════════════════════════════════╗
      ║                    ═══ CHRISTOPHER BOETTE ═══                        ║
      ║                     Senior Software Engineer                         ║
      ║  ════════════════════════════════════════════════════════════════    ║
      ║                 ╔═══════╗ ╔════════╗ ╔════════╗                      ║
      ║                 ║ AI/ML ║ ║Platform║ ║DevTools║                      ║
      ║                 ╚═══════╝ ╚════════╝ ╚════════╝                      ║
      ║  ════════════════════════════════════════════════════════════════    ║
      ║  │ data.world acq by ServiceNow (2019-now)                           ║
      ║  │ ◆ AI product integration  ◆ LLM eval infrastructure               ║
      ║  │ ◆ Full-stack platform (data catalog)  ◆ Dev tooling & APIs        ║
      ║  │                                                                   ║
      ║  │ Volusion (2017-19)                                                ║
      ║  │ ◆ Open-source CLI  ◆ Dev platform  ◆ React architecture           ║
      ║  │                                                                   ║
      ║  │ OwnLocal (2016-17)                                                ║
      ║  │ ◆ React & AWS Lambda  ◆ AWS Auth stack  ◆ ELK stack               ║
      ║  |                                                                   ║
      ║  | Wikibuy (2015-16)                                                 ║
      ║  | ◆ Lodash & Cheerio scripts  ◆ Slackbot POC                        ║
      ║  |                                                                   ║
      ║  | GameSalad (2014-15)                                               ║ 
      ║  | ◆ Rails  ◆ AngularJS & nodejs  ◆ Too much Perl                    ║
      ║  ════════════════════════════════════════════════════════════════    ║
      ║  TypeScript · React · Node · Python · AWS · LLM · System Design      ║
      ║  ════════════════════════════════════════════════════════════════    ║
      ║   ◆───── https://newschematic.org · github.com/chrisbodhi ─────◆     ║
      ╚══════════════════════════════════════════════════════════════════════╝
```

It's a terse reading of a career, maybe even scant. Its width is optimized for the screen, not for the letter-page width. Editing the thing is finicky, but brainless. In the document, there are some plain-text URL's, but no affordances for hyperlinks, like HTML. Maybe it's served over `plain/text` or maybe it's on Gopher. Maybe it ends on a message board or a listserv or Usenet. Content-wise, "nuance" doesn't even get a passing thought.

But, we ended up with smartphones, eye-drugs aren't mainstream, and we're on the verge of letting a million-million agents bloom. What does a resume look like in the next year, when agents are out sourcing leads for recruiters or evaluating candidates for fit, in squishy ways? What do the agents do for a field where "taste" means "I've seen enough cuts of jibs to know who's going to succeed in this kind of role"?

Thinking mechanically, our LLM friends like to read and write Markdown, and it's also human-readable. But, it's easier to blow out a context window when you're reproducing your meticulously-crafted LinkedIn profile that has to speak to three different audiences. We could adapt the [`llms.txt`](https://llmstxt.org/#format) proposal for job searchers, a less-visible way for blog owners to signal that they're open to work. But, not everyone has a blog. We also need to make them discoverable and keep the status on those text files up-to-date; there's already 101 things to do in a job search, and they're all in your face but updating a text file only read by agents is, by design, not in your face.

The mechanical questions are all answerable, even faster now than before. The thorny parts are always outside the realm of bits and bytes. What do you gain when Linkedin withers away and is replaced by autonomous agents crawling directories of job-searchers? (_Everything_) What happens when those agents start crawling personal, political, or apoplectic posts from one, ten, twenty years ago, and then surface them as causes for concern, or outright rejection? A person does that, we'll never know; it's deniable. A properly auditable and observable agent program will tell you exactly which anti-discrimination laws it violated, apologize, and then promise to never do that again (_This may be solved by harnesses, but it remains to be seen_)

Yeah, thorny.

### Unbias Me

>Displays GitHub, LinkedIn and Twitter profiles with minimal attribution information.
>Trying to improve your hiring practices and increase diversity at your workplace? Reduce room for unconscious bias when reviewing job candidates' online materials.

Almost a decade ago, I submitted a PR to this Chrome extension that helped hide some identifiable information about users on web platforms. It's strange that we want people to put up pictures of themselves on platforms like GitHub, but then let ourselves be influenced how they look, rather than the work that is also directly in front of us (I guess this is why there's been a proliferation of anime pfp's). Anyway, I opened the PR, got feedback from a passerby, made some changes, and then silence from the maintainer. I don't remember if this is the first time this has happened to me, but it was only a little annoying.

It seems like that this vision could now be realized, but I fear that the people who would be most onboard with a maximally-useful version of this browser extension would be h o r r i f i e d that an LLM helped them find their next hire. Is there nothing to do for them?

### Where are you going with this?

A proposal for a new standard format, modeled after `llms.txt`:

```txt
> ISO senior/staff engineering roles at Series B+ startups

Candidate has a family to support, so is going to push for more compensation in salary than in options. They're a big believer in causes, and your cause specifically, so don't read it the wrong way when they don't want more options instead of dollars.
```
