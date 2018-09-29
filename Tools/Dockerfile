FROM ubuntu:bionic
LABEL maintainer="pfadfinder@jonashoechst.de"
LABEL description="A docker image for build the Pfadiralala IV VCP Kurhessen (german scouts) songbook."
LABEL version="1.0"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
    && apt-get install -y \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-extra-utils \
        texlive-lang-german \
        xzdec \
        abcm2ps \
        ghostscript \
        make \
    && apt-get clean

RUN mkdir /PfadiralalaIV
WORKDIR /PfadiralalaIV