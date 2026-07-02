FROM python:3.12.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc-11 g++-11 build-essential cmake git curl gnupg2 ninja-build openjdk-17-jre-headless \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 60 \
                           --slave /usr/bin/g++ g++ /usr/bin/g++-11 \
    && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /root/.tika && \
    curl -L -o /root/.tika/tika-server.jar https://downloads.apache.org/tika/tika-server-2.9.1.jar

COPY requirements.txt .

RUN pip install "pip<24.1" && \
    pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader stopwords punkt_tab wordnet

COPY . .

EXPOSE 8230

COPY ./scripts/entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]