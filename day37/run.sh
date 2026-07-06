#!/usr/bin/env bash
# Day 37 · 委托 Project 2 一键启动
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")/../day36/code/project2" && pwd)/run.sh" "$@"
