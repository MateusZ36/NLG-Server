# NLG-Server

## O Que é

o NLG Server é utilizado como um seletor de respostas baseado em `templates` para o [Rasa](https://github.com/RasaHQ/rasa), fazendo com que não há necessidade de retreinar o bot para que as alterações das `responses` façam efeito


##  Utilização

### Instalação e Execução

É recomendável utilizar um [ambiente virtual](https://docs.python.org/3.8/tutorial/venv.html)

comandos para instalação de dependências e execução do servidor:
```sh
pip install -r requirements.txt
python server.py
``` 

### Argumentos
 - `-d` ou `--domain`: localizaçao dos arquivos (padrão: `.`)
 - `-p` ou `--port`: port utilizado pelo server (padrão: `5065`)
 - `-w` ou `--workers`: quantia de workers a serem utilizados (padrão: `1`)
 - `--nlg`: caminho da classe de NLG customizada a ser carregada (padrão: `TemplatedNaturalLanguageGenerator`)

### Importação de arquivos
Para importar o arquivo de responses, basta colocar os arquivos na pasta especificada no parâmetro `-d` 

### Utilizando no Rasa
No arquivo `endpoints.yml` do Rasa, adicione a seguinte configuração:
```yml
nlg:
  url: http://localhost:5056/nlg
```

#### NLG Customizado
Para utilizar um NLG diferente, basta passar por parâmetro ao inicializar o serviço, exemplo:
```shell
python server.py --nlg generator.CustomNLG
```

#### Endpoint `/reload`

Também há a possibilidade de recarregar o domain ao fazer um request `GET` no endpoint `/reload`
<details>
<summary>Exemplo de resposta de <code>/reload</code></summary>

```json
{
 "text":"Loaded 6 responses",
 "domain_path":"."
}
```
</details>

<details>
<summary>Exemplo de resposta de <code>/reload?show_responses=title</code></summary>

```json
{
 "text":"Loaded 6 responses",
 "domain_path":".",
 "responses":[
  "utter_greet",
  "utter_cheer_up",
  "utter_did_that_help",
  "utter_happy",
  "utter_goodbye",
  "utter_iamabot"
 ]
}
```
</details>

<details>
<summary>Exemplo de resposta de <code>/reload?show_responses=full</code></summary>

```json
{
 "text":"Loaded 6 responses",
 "domain_path":".",
 "responses":{
  "utter_greet":[
   {
    "text":"Hey! How are you?"
   }
  ],
  "utter_cheer_up":[
   {
    "text":"Here is something to cheer you up:",
    "image":"https:\/\/i.imgur.com\/nGF1K8f.jpg"
   }
  ],
  "utter_did_that_help":[
   {
    "text":"Did that help you?"
   }
  ],
  "utter_happy":[
   {
    "text":"Great, carry on!"
   }
  ],
  "utter_goodbye":[
   {
    "text":"Bye"
   }
  ],
  "utter_iamabot":[
   {
    "text":"I am a bot, powered by Rasa."
   }
  ]
 }
}
```
</details>
