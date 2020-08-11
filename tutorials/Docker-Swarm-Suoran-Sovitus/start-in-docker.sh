#!/usr/bin/env bash
docker run -p 8888:8888 --user root -e JUPYTER_ENABLE_LAB=yes -e GRANT_SUDO=yes -v $(pwd):/home/jovyan/work jupyter/scipy-notebook:latest
