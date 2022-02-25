# NLG-Server


##Utilização

###Instalação e Execução
É recomendável utilizar um ambiente virtual

comandos para instalação de dependências e execução do servidor:
```sh
pip install -r requirements.txt
python server.py
``` 

###Argumentos
 - `-d` ou `--domain`: localizaçao dos arquivos (padrão: `.`)
 - `-p` ou `--port`: port utilizado pelo server (padrão: `5065`)
 - `-w` ou `--workers`: quantia de workers a serem utilizados (padrão: `1`)