import requests
import json
import urllib.parse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from s3_utils import upload_file
import os

dict_brcobranca_bank = {
    '001': 'banco_brasil',
    '041': 'banrisul',
    '237': 'bradesco',
    '104': 'caixa',
    '399': 'hsbc',
    '341': 'itau',
    '033': 'santander',
    '748': 'sicred',
    '004': 'banco_nordeste',
    '021': 'banestes',
    '756': 'sicoob',
    '136': 'unicred',
}

dict_brcobranca_currency = {
    'R$': '9'
}


@api_view(['POST'])
def generate(request):
    data = JSONParser().parse(request)
    boleto = {
        'valor': str("%.2f" % data['valor']),
        'cedente': data['cedente'],
        'documento_cedente': data['documento_cedente'],
        'cedente_endereco': data.get('cedente_endereco', ''),
        'sacado': data['sacado'],
        'sacado_documento': data['sacado_documento'],
        'sacado_endereco': data.get('sacado_endereco', ''),
        'agencia': data['agencia'],
        'conta_corrente': data['conta_corrente'],
        'convenio': data['convenio'],
        'nosso_numero': data['nosso_numero'],
        'documento_numero': data.get('documento_numero', ''),
        'especie': data.get('especie', 'R$'),
        'especie_documento': data.get('especie_documento', 'DM'),
        'moeda': dict_brcobranca_currency['R$'],
        'aceite': data.get('aceite', 'S'),
        'instrucao1': data.get('instrucao1', '')
    }

    if 'data_vencimento' in data:
        boleto.update({'data_vencimento': data.get('data_vencimento')})

    if 'data_documento' in data:
        boleto.update({'data_documento': data.get('data_documento')})

    if 'data_processamento' in data:
        boleto.update({'data_processamento': data.get('data_processamento')})

    # JUROS
    boleto_perc_mora = data.get('boleto_perc_mora', 0)
    if boleto_perc_mora > 0.0:
        instrucao_juros_tmp = "APÓS VENCIMENTO COBRAR PERCENTUAL"
        if 'instrucao_boleto_perc_mora' in data:
            instrucao_juros_tmp = data['instrucao_boleto_perc_mora']
        valor_porcentagem = (boleto_perc_mora / 100)
        valor_juros = round(data['valor'] * (valor_porcentagem / 30), 2)
        instrucao_juros = (
                instrucao_juros_tmp +
                " DE %s %% AO MÊS ( R$ %s AO DIA )"
                % (('%.2f' % boleto_perc_mora).replace('.', ','),
                   ('%.2f' % valor_juros).replace('.', ',')))
        boleto.update({'instrucao3': instrucao_juros})

    # MULTA
    boleto_perc_multa = data.get('boleto_perc_multa', 0)
    if boleto_perc_multa > 0.0:
        instrucao_multa_tmp = "APÓS VENCIMENTO COBRAR PERCENTUAL"
        if 'instrucao_boleto_perc_multa' in data:
            instrucao_multa_tmp = data['instrucao_boleto_perc_multa']
        valor_porcentagem = (boleto_perc_multa / 100)
        valor_multa = round(data['valor'] * valor_porcentagem, 2)

        instrucao_multa = (
                instrucao_multa_tmp +
                " DE %s %% ( R$ %s )" %
                (('%.2f' % boleto_perc_multa
                  ).replace('.', ','),
                 ('%.2f' % valor_multa).replace('.', ',')))
        boleto.update({'instrucao4': instrucao_multa})

    # DESCONTO
    discount_perc = data.get('discount_perc', 0)
    if discount_perc > 0.0:
        instrucao_desconto_vencimento_tmp = 'CONCEDER ABATIMENTO PERCENTUAL DE'
        if 'instrucao_discount_perc' in data:
            instrucao_desconto_vencimento_tmp = data['instrucao_discount_perc']
        valor_porcentagem = (discount_perc / 100)
        valor_desconto = round(data['valor'] * valor_porcentagem, 2)
        instrucao_desconto_vencimento = (
                instrucao_desconto_vencimento_tmp + ' %s %% '
                                                    'ATÉ O VENCIMENTO EM %s ( R$ %s )'
                % (('%.2f' % discount_perc
                    ).replace('.', ','),
                   data.get('date_vencimento', '01/01/2020').strftime('%d/%m/%Y'),
                   ('%.2f' % valor_desconto).replace('.', ',')
                   ))
        boleto.update({'instrucao5': instrucao_desconto_vencimento})

    # if bank_account.bank_id.code_bc in ('021', '004'):
    #     boleto_cnab_api_data.update({
    #         'digito_conta_corrente':
    #             move_line.payment_mode_id.bank_id.acc_number_dig,
    #     })
    #
    # # Fields used in Sicredi/Unicred and Sicoob Banks
    # if bank_account.bank_id.code_bc == '748':
    #     boleto_cnab_api_data.update({
    #         'byte_idt': move_line.payment_mode_id.boleto_byte_idt,
    #         'posto': move_line.payment_mode_id.boleto_posto,
    #     })

    data_url_encoded = urllib.parse.quote(json.dumps(boleto))
    boleto_api_url = os.getenv('BOLETO_API_URL')
    boleto_api_port = os.getenv('BOLETO_API_PORT')
    api_service_address = boleto_api_url + ':' + boleto_api_port + '/api/boleto?type=pdf&bank=' + data[
        'banco'] + '&data=' + data_url_encoded
    res = requests.get(api_service_address)

    if str(res.status_code)[0] == '2':
        pdf_string = res.content
        file_name = 'boleto' + boleto['documento_numero'] + '.pdf'
        with open(file_name, 'wb') as file:
            file.write(pdf_string)
        with open(file_name, 'rb') as file:
            upload_file(file_name, file)
            os.remove(file_name)
    else:
        raise Exception(res.text.encode('utf-8'))
    return Response({"message": "Boleto criado.", "boleto_name": file_name})
