import json, os, requests, datetime
from datetime import date
from requests import Session
from requests.exceptions import HTTPError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from flask import Flask, flash, request

class Simulate():

    def __init__(self):
        super().__init__()
        self.simulate = self.build_simulate_session()
    
    @staticmethod
    def build_simulate_session():
        session = Session()

        num_retries = int(os.getenv('simulate_retries', '3'))
        backoff_factor = float(os.getenv('simulate_backoff_factor', '0.3'))
        connections_pool_size = int(os.getenv('simulate_pool_size', '3'))
        connections_pool_max_currency = int(os.getenv('connections_pool_max_currency', '3'))

        retry_policy = Retry(
            total=num_retries,
            read=num_retries,
            connect=num_retries,
            backoff_factor=backoff_factor,
        )

        adapter = HTTPAdapter(
            max_retries=retry_policy,
            pool_connections=connections_pool_size,
            pool_maxsize= connections_pool_max_currency,
        )

        session.mount('http://', adapter)
        session.mount('https://', adapter)

        session.headers.update({
            'User-Agent': 'SimulateClient/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        return session
    
    def simulate_recipe(self, brute_income, initial_application, contributions_monthly,
                            date_retireday, spent_monthly, validate_bank, application_type, method):
        try:
            """
            Calcula a renda máxima aplicável mensal. 
            Ao qual limit_total_income é o resultado do calculo entre brute_income que é (a renda bruta atual) multiplicado por
             12 (meses) , multiplicado por 12% e por fim dividio por 12 meses resultando quanto é o máximo possível para investir por mês.
            """
            limit_total_income = ((brute_income * 12) * 12 / 100) / 12
            
            # Verifica se a renda aplicável mensal é menor ou igual a limit_total_income
            if limit_total_income <= contributions_monthly:
                # Define o número de meses por ano
                monthlys_per_year = 12

                # Obtém a data de hoje e o ano atual
                today_date = date.today()
                current_year = today_date.year

                # Calcula a quantidade de anos até a aposentadoria
                quantity_years = date_retireday - current_year
                
                # Calcula a quantidade de meses até a aposentadoria
                quantity_months = quantity_years * monthlys_per_year

                if validate_bank:
                    """
                    fixed_income é Renda fixa,
                    variable_income é Renda Variável 
                    multi_market é Mercado de ações
                    tax_administrative é a taxa administrativa daquela aplicação mensal 
                    """
                    bank_application_mapping = {
                        'fixed_income': (12 / 100) / 12, 
                        'variable_income': (13 / 100) / 12, 
                        'multi_market': (14 / 100) / 12, 
                        'tax_administrative': (0.99 / 100) 
                    }

                    # Conforme a opção selecionada pelo usuário na application_type, eu pesquiso no dicionario o primeiro valor igual 
                    selected_application_type = bank_application_mapping.get(application_type, 0)
                    # Como se trata de uma simulação com a opção Banco ativa, eu pego o valor do dicionário da taxa administrativa
                    tax_administrative = bank_application_mapping['tax_administrative']

                    # Inicializa o primeiro montante
                    total_amount = initial_application + contributions_monthly

                    # Loop para calcular o montante ao longo dos meses com aportes mensais e juros
                    for i in range(1, quantity_months):  # Começa a partir do segundo mês
                        # Adiciona o aporte mensal (a partir do segundo mês)
                        total_amount += contributions_monthly
                        # Aplica os juros sobre o montante acumulado
                        total_amount += total_amount * (selected_application_type)

                    # Calcula o montante do primeiro mês
                    first_month_money = (initial_application + contributions_monthly) * selected_application_type

                    # Calcula o total de contribuições ao longo dos anos usando juros compostos anuais
                    contribution_total = (initial_application + contributions_monthly) * ((1 + selected_application_type) ** quantity_years - 1) / selected_application_type

                    # Calcula o montante total após descontar a taxa administrativa
                    total_money = (first_month_money + contribution_total) * (1 - tax_administrative)

                    # Calcula o total gasto ao longo dos anos
                    spent_total_per_years = total_money / (spent_monthly * monthly_per_year)

                    result = {
                        'first_month_money': first_month_money,
                        'contribution_total': contribution_total,
                        'total_money': total_money,
                        'spent_total_per_years': spent_total_per_years
                    }

                    return result
                else:
                    return {
                        'error': 'Banco não marcado ou taxa de aplicação não disponível.'
                    }
            else:
                monthly_per_year = 12
                today_date = date.today()
                current_year = today_date.year
                quantity_years = date_retireday - current_year

                if validate_bank:
                    bank_application_mapping = {
                        'fixed_income': 12.50 / 100, 
                        'variable_income': 13 / 100, 
                        'multi_market': 14 / 100, 
                        'tax_administrative': 0.99 / 100
                    }

                    selected_application_type = bank_application_mapping.get(application_type, 0)
                    tax_administrative = bank_application_mapping['tax_administrative']

                    first_month_money = (initial_application + contributions_monthly) * (1 + selected_application_type)
                    contribution_total = (initial_application + contributions_monthly) * ((1 + selected_application_type) ** quantity_years - 1) / selected_application_type
                    total_money = (first_month_money + contribution_total) * (1 - tax_administrative)
                    spent_total_per_years = total_money / (spent_monthly * monthly_per_year)

                    result = {
                        'first_month_money': first_month_money,
                        'contribution_total': contribution_total,
                        'total_money': total_money,
                        'spent_total_per_years': spent_total_per_years
                    }

                    return result
                else:
                    return {
                        'error': 'Banco não validado ou taxa de aplicação não disponível.'
                    }

        except KeyError as ke:
            return {'error': f'Erro de chave no mapeamento: {ke}'}
        except ValueError as ve:
            return {'error': f'Erro de valor: {ve}'}
        except TypeError as te:
            return {'error': f'Erro de tipo de dado: {te}'}
        except Exception as e:
            return {'error': f'Ocorreu um erro inesperado: {e}'}