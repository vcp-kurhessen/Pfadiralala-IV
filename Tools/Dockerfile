FROM ubuntu:bionic as abcm2ps_builder

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        make \
        gcc \
        libc6-dev \
    && apt-get clean

WORKDIR /tmp/
ADD https://github.com/leesavide/abcm2ps/archive/v8.14.1.tar.gz abcm2ps-8.14.1.tar.gz
RUN tar -xf abcm2ps-8.14.1.tar.gz

WORKDIR /tmp/abcm2ps-8.14.1/
RUN ./configure
RUN make install


FROM ubuntu:bionic
LABEL maintainer="pfadfinder@jonashoechst.de"
LABEL description="A docker image for build the Pfadiralala IV VCP Kurhessen (german scouts) songbook."
LABEL version="1.1"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-extra-utils \
        texlive-lang-german \
        xzdec \
        ghostscript \
        make \
        lua5.3 \
    && apt-get clean

RUN mkdir /PfadiralalaIV
WORKDIR /PfadiralalaIV

COPY --from=abcm2ps_builder /usr/local/bin/abcm2ps /usr/local/bin/
