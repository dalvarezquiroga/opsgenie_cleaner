# Base image to be used
FROM ubuntu:20.04

# Environment Variables
ENV TERM linux
ENV DEBIAN_FRONTEND noninteractive

# Input data
ENV OPSGENIE_LAMP_VERSION=3.1.4
ARG NON_ROOT_USER=nroot

# Change to ROOT user to do maintenance/install tasks
USER root

# Working directory
WORKDIR /tmp

# Install packages
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip \
    git \
    wget \
    jq \
    curl \
    unzip \
    gnupg \
    bash

# Check versions
RUN python3 -V

# Cleanup
RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y

# Copy requirements.txt file to workdir
COPY requirements.txt /tmp/

# Install pip components from requirements.txt
RUN pip3 install -r requirements.txt

# Install OPSGENIE LAMP
RUN curl -L https://github.com/opsgenie/opsgenie-lamp/releases/download/v${OPSGENIE_LAMP_VERSION}/opsgenie-lamp_${OPSGENIE_LAMP_VERSION}_linux_amd64.zip > /tmp/opsgenie-lamp.zip \
    && cd /tmp && ls && unzip opsgenie-lamp.zip && mv opsgenie-lamp_v${OPSGENIE_LAMP_VERSION} /usr/local/bin/opsgenie-lamp && chmod +x /usr/local/bin/opsgenie-lamp && rm -rf /tmp/opsgenie-lamp*

# Check versions
RUN opsgenie-lamp --version

# Clean up tmp directory
RUN rm --recursive --force -- *

# Create a non-root user
RUN useradd --create-home --shell /bin/bash ${NON_ROOT_USER} && su - ${NON_ROOT_USER}

# Use non-root user
USER ${NON_ROOT_USER}

# Set workdir to user home
WORKDIR /home/${NON_ROOT_USER}

# Configure SSH client
RUN mkdir -p /home/${NON_ROOT_USER}/.ssh && \
    chmod 700 /home/${NON_ROOT_USER}/.ssh && \
    printf "Host *\\n\\tStrictHostKeyChecking no\\n\\n" > /home/${NON_ROOT_USER}/.ssh/config

# Copy opsgenie_cleaner.py script to HOME.
COPY opsgenie_cleaner.py /home/${NON_ROOT_USER}

# Command to execute
CMD ["bash"]
