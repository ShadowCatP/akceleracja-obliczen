#!/bin/sh

check_command() {
	if ! command -v "$1" >/dev/null 2>&1; then
		echo "error: required command not found: $1" >&2
		exit 1
	fi
}

check_command git
check_command g++

git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

echo "project configured"