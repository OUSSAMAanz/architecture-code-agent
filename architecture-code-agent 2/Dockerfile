FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml requirements.txt README.md ./
COPY code_agent ./code_agent
COPY inputs ./inputs
RUN pip install --no-cache-dir .

ENTRYPOINT ["architecture-code-agent"]
CMD ["--help"]
