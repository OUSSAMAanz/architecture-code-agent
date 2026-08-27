# Submission Checklist

## Before uploading

- [ ] Run `python -m unittest discover -s tests -v` and capture the result.
- [ ] Run the scripted generation command from the README.
- [ ] Run `npm test` inside the generated repository.
- [ ] Read the README and research notes so you can explain the design yourself.
- [ ] Replace the GitHub description with your own name/course details if required.
- [ ] Confirm that `.env` and API keys are not present in Git.

## Suggested GitHub commands

Create an empty repository on GitHub first, then run these commands from this
directory. Replace the example URL with your repository URL.

```bash
git init
git add .
git commit -m "Implement architecture-driven Code Agent"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/architecture-code-agent.git
git push -u origin main
```

## Suggested message to the teacher

> Dear Peng,
>
> Please find my Task 1 implementation here: [GitHub repository URL]. The project
> implements an independent OpenAI Codex-powered Code Agent with structured
> Markdown/PlantUML parsing, a model/tool loop, safe workspace tools, automated
> tests, and a generated Space Fractions example. I have also included research on
> Claude Code's implementation mechanisms and full usage instructions.
>
> Demo video: [optional video URL]
>
> Best regards,  
> Oussama

## Video

Use `docs/DEMO_SCRIPT.md` as a three-minute recording outline. Do not display an
API key, terminal history containing secrets, email addresses, or private browser
tabs while recording.
