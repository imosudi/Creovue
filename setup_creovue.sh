#!/bin/bash

set -e

PROJECT_ROOT="Creovue"

create_dir() {
  [ ! -d "$1" ] && mkdir -p "$1"
}

create_file() {
  local file="$1"
  shift
  if [ ! -f "$file" ]; then
    cat <<EOF > "$file"
$@
EOF
  fi
}

echo "🔧 Creating Creovue project scaffold..."

# Create root directory
create_dir "$PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Top-level files
create_file "app.py" '#!/usr/bin/env python3

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
'

create_file "config.py" '"""App configuration module."""'

create_file "requirements.txt" 'Flask
requests
pandas
scikit-learn
opencv-python
'

create_file "Makefile" 'run:
\tpython3 app.py

test:
\tpytest tests/

lint:
\tflake8 . --exclude=venv,__pycache__
'

create_file "README.md" '# Creovue

Creovue is a YouTube analytics and SEO tool for individual creators and SMBs.'

create_file "run.sh" '#!/bin/bash
python3 app.py'
chmod +x run.sh

# Python package folders and modules
declare -A MODULES=(
  ["models"]="seo.py analytics.py thumbnail.py competitor.py trends.py"
  ["ml"]="predictor.py thumbnail_model.py"
  ["scheduler"]="update_metrics.py trend_monitor.py"
  ["utils"]="auth.py yt_api.py data_helpers.py"
  ["db"]="init_db.py"
  ["tests"]="test_seo.py test_analytics.py test_thumbnail.py"
)

for dir in "${!MODULES[@]}"; do
  create_dir "$dir"
  create_file "$dir/__init__.py" '"""Init file."""'
  for file in ${MODULES[$dir]}; do
    create_file "$dir/$file" '"""Module: '$file'."""'
  done
done

# schema.sql
create_file "db/schema.sql" '-- SQL schema definition for Creovue'

# Static assets
create_dir "static/css"
create_dir "static/js"
create_dir "static/images"

# HTML templates
create_dir "templates"
create_file "templates/base.html" '<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}Creovue{% endblock %}</title>
</head>
<body>
  {% block content %}{% endblock %}
</body>
</html>'

for name in dashboard seo analytics trends; do
  create_file "templates/${name}.html" '{% extends "base.html" %}
{% block title %}'"${name^}"' | Creovue{% endblock %}
{% block content %}
<h2>'"${name^}"' Page</h2>
<p>Content for '"${name^}"'.</p>
{% endblock %}'
done

# Docker
create_dir "docker"

create_file "docker/Dockerfile" 'FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "app.py"]
'

create_file "docker/docker-compose.yml" 'version: "3"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
'

echo "✅ Creovue project scaffold created successfully in $(pwd)"
