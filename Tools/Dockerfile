FROM ubuntu:bionic

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
