import os
my_secret = os.environ['type']
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from flask import Flask
from flask import request
app = Flask(__name__)


def create_keyfile_dict():
  variables_keys = {
    "type": os.getenv("type"),
    "project_id": os.getenv("project_id"),
    "private_key_id": os.getenv("private_key_id"),
    "private_key": os.getenv("private_key"),
    "client_email": os.getenv("client_email"),
    "client_id": os.getenv("client_id"),
    "auth_uri": os.getenv("auth_uri"),
    "token_uri": os.getenv("token_uri"),
    "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
    "client_x509_cert_url": os.getenv("client_x509_cert_url")
  }
  return variables_keys

scope = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(create_keyfile_dict(), scope)
client  = gspread.authorize(creds)
spreadsheetName = "testePython-sheets"
spreadsheet = client.open(spreadsheetName)


##################################################
def separarNomes(nome,nomes,quantidadeNomes):
  if quantidadeNomes == 0:
    return [nome]
  arrayNomes = [nome]
  arrayNomes += nomes.split(sep=",")
  if arrayNomes[len(arrayNomes)-1] == '':
    arrayNomes.pop()
  return arrayNomes

def inscricao(nome,culto):
  req = request.get_json(silent=True, force=True)
  query_result = req.get('queryResult')
  if culto.lower() == "9h":
    infoInscricao = spreadsheet.get_worksheet(1)
  elif culto.lower() == "11h":
    infoInscricao = spreadsheet.get_worksheet(2)
  if culto.lower() == "18h30":
    infoInscricao = spreadsheet.get_worksheet(3)
  
  nomes = separarNomes(nome,query_result.get('parameters').get('nomesAcompanhantes'),query_result.get('parameters').get('numPessoas'))
  for i in range(0, len(nomes)):
    pessoa = [
                  nomes[i],
                  query_result.get('parameters').get('email'),
                  query_result.get('parameters').get('telefone'),
                  query_result.get('parameters').get('primeiraVez') 
              ]
    insertRow = [pessoa[0],pessoa[1],pessoa[2],pessoa[3]]
    infoInscricao.append_row(insertRow, table_range="A2")
##################################################


@app.route('/')
def hello_world():
  return "Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    fulfillmentText = ''
    query_result = req.get('queryResult')


    if query_result.get('action') == 'documentosImportantes':
        boletim = spreadsheet.get_worksheet(4) #pega a 4 planilha do sheet
        escolha = query_result.get('parameters').get('escolha')
        if escolha == 1:
            fulfillmentText = boletim.cell(2,1).value
        elif escolha == 2:
            fulfillmentText = boletim.cell(2,2).value
        elif escolha == 3:
            fulfillmentText = boletim.cell(2,3).value
        elif escolha == 4:
            fulfillmentText = boletim.cell(2,4).value
        else:
            fulfillmentText = "Valor inválido"
        fulfillmentText += "\nCaso deseja finalizar, digite FIM.\nCaso queira voltar, digite VOLTAR."

    if query_result.get('action') == 'inscricao':
      confirma = query_result.get('parameters').get('confirma').lower()
      if confirma == 'sim':
        nomeResponsavel = query_result.get('parameters').get('nome')
        culto = query_result.get('parameters').get('culto')
        numPessoas = int(query_result.get('parameters').get('numPessoas'))
        nomes = query_result.get('parameters').get('nomesAcompanhantes')
        inscricao(nomeResponsavel, culto)
        fulfillmentText = "Sua inscrição foi realizada.\nSe quiser finalizar, digite FIM.\nCaso queira voltar  ao menu, digite VOLTAR."
      else:
        fulfillmentText = "Caso deseja finalizar, digite FIM.\nCaso queira voltar, digite VOLTAR."


    return {
        "fulfillmentText": fulfillmentText,
        "source": 'webhook'
    }

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)