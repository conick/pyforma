# pyForma

Requirements

* Python 3.9+

## Setup

Open cli and go to folder what shoud store pyforma project

```bash
cd /Projects
```

Get repo and initialize git

```bash
git clone https://github.com/conick/pyforma
cd pyforma
git init
```

Create and activate virtual env (it is optional, you can use global packages configuration)

```bash
python3 -m venv env
./env/bin/activate
```

Install packages by pip

```bash
pip3 install -r requirements.txt
```

Additional for winservice:

```bash
pip3 install pywin32
```

Copy `config-template.yaml` as `config.yaml` and setup last one

## Run

```bash
python3 src/main.py
```

## Check version

```bash
git describe --tags
```
