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
    
    def simulate_recipe_bank(self, brute_income, initial_application, contributions_monthly, date_retireday, spent_monthly, validate_bank, application_type, method):
        # Calcula a renda máxima aplicavél caso passe de 12% da renda bruta se encaixa em VGBL
        limit_total_income = brute_income * 12/100
        # Verifica se a renda aplicavél é menor ou igual a 12% da renda bruta
        if limit_total_income <= contributions_monthly and method == 'PGBL':
            # Define o número de meses por ano
            monthly_per_year = 12

            # Obtém a data de hoje e o ano atual
            today_date = date.today()
            current_year = today_date.year

            # Calcula a quantidade de anos até a aposentadoria
            quantity_years = date_retireday - current_year

            if validate_bank:

                # Mapeia as taxas de aplicação para diferentes bancos
                bank_application_mapping = {
                    'fixed_income': 12.50 / 100, 
                    'variable_income': 13 / 100, 
                    'multi_market': 14 / 100, 
                    'tax_administrative': 0.99 / 100
                }

                # Obtém a taxa de aplicação e a taxa administrativa do dicionário
                application_rate = bank_application_mapping.get(application_type, 0)
                tax_administrative = bank_application_mapping['tax_administrative']

                # Calcula o montante do primeiro mês
                first_month_money = (initial_application + contributions_monthly) * (1 + application_rate)

                # Calcula o total de contribuições ao longo dos anos usando juros compostos anuais
                contribution_total = (initial_application + contributions_monthly) * ((1 + application_rate) ** quantity_years - 1) / application_rate

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
                # Caso validate_bank seja False, você pode retornar algum valor padrão ou mensagem
                return {
                    'error': 'Banco não marcado ou taxa de aplicação não disponível.'
                }
        else:
            # Define o número de meses por ano
            monthly_per_year = 12

            # Obtém a data de hoje e o ano atual
            today_date = date.today()
            current_year = today_date.year

            # Calcula a quantidade de anos até a aposentadoria
            quantity_years = date_retireday - current_year

            if validate_bank:

                # Mapeia as taxas de aplicação para diferentes bancos
                bank_application_mapping = {
                    'fixed_income': 12.50 / 100, 
                    'variable_income': 13 / 100, 
                    'multi_market': 14 / 100, 
                    'tax_administrative': 0.99 / 100
                }

                # Obtém a taxa de aplicação e a taxa administrativa do dicionário
                application_rate = bank_application_mapping.get(application_type, 0)
                tax_administrative = bank_application_mapping['tax_administrative']

                # Calcula o montante do primeiro mês
                first_month_money = (initial_application + contributions_monthly) * (1 + application_rate)

                # Calcula o total de contribuições ao longo dos anos usando juros compostos anuais
                contribution_total = (initial_application + contributions_monthly) * ((1 + application_rate) ** quantity_years - 1) / application_rate

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
                # Caso validate_bank seja False, você pode retornar algum valor padrão ou mensagem
                return {
                    'error': 'Banco não validado ou taxa de aplicação não disponível.'
                }