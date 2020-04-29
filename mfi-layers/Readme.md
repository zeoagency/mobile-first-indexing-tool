# Mobile First Indexing - AWS Lambda Layers

This package supports Python 3.6
 
## Structure

```bash
── mfi-layers/
  ├── selenium
  │  └──/python/
  │   └── /lib/
  │     └── /python3.6/*
  ├── chromedriver/
  │ ├── /chromedriver
  │ └── /headless-chromium
  ├── bs4
  │  └──/python/
  │   └── /lib/
  │     └── /python3.6/*
  ├── extruct
  │  └──/python/
  │   └── /lib/
  │     └── /python3.6/*
  ├── lxml
  │  └──/python/
  │   └── /lib/
  │     └── /python3.6/*
  ├── requests
  │  └──/python/
  │   └── /lib/
  │     └── /python3.6/*
  ├── w/3lib
  │  └──/python/
  │   └── /lib/
  │     └── /python3.6/*
  └── serverless.yaml
```

## Packages Manual Instalation

For pip packages

```shell script

$  pip install -t selenium/python/lib/python3.6/site-packages selenium=2.37
$  pip install -t w3lib/python/lib/python3.6/site-packages w3lib
$  pip install -t extruct/python/lib/python3.6/site-packages extruct
$  pip install -t bs4/python/liab/python3.6/site-packages bs4
$  pip install -t requests/python/liab/python3.6/site-packages requests
$  pip install -t lxml/python/liab/python3.6/site-packages lxml
```

For other
```
$ cd chromedriver
$ curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
$ unzip chromedriver.zip
$ curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-41/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
$ unzip headless-chromium.zip
$ rm headless-chromium.zip chromedriver.zip
```

## Deploy Lambda Layers
Go to root directory of project.
```bash
$ sls deploy
```

