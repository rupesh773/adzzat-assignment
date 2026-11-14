FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends gfortran python3 python3-pytest && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY payroll.f90 /app/payroll.f90
COPY hours.txt /app/hours.txt
