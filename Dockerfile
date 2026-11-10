FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/KintanaOne/Toetra"

WORKDIR /app

COPY pyproject.toml MANIFEST.in ./
COPY README.md LICENSE COPYRIGHT.md COMMERCIAL_LICENSE.md CHANGELOG.md THIRD_PARTY.md ./
COPY src/ ./src/

RUN python -m pip install --no-cache-dir .

ENTRYPOINT ["toetra"]
CMD ["--help"]