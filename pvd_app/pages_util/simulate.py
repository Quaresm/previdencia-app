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
    
    def simulate_recipe_bank(self, initial_application, contributions_monthly, date_retireday, spent_monthly, bank, application_type, method, total_income):
        limit_total_income = total_income * 12/100
        if limit_total_income <= contributions_monthly and method == 'PGBL':
            monthly_per_year = 12
            today_date = date.today()
            current_year = today_date.year
            quantity_years = date_retireday - current_year

            bank_application_mapping = {
                'Itau': {'fixed_income': 12.30/100, 'variable_income': 14/100 , 'multi_market':15/100,'tax_administrative':0.95/100},
                'Santander': {'fixed_income': 12.50/100, 'variable_income': 13/100, 'multi_market': 14/100, 'tax_administrative': 0.99/100},
                'Bradesco': {'fixed_income': 12.85/100, 'variable_income': 12/100, 'multi_market': 13/100, 'tax_administrative': 0.98/100},
                'Banco_do_Brasil': {'fixed_income': 12/100, 'variable_income': 11/100, 'multi_market': 12/100, 'tax_administrative': 1/100}
            }

            if bank in bank_application_mapping and application_type in bank_application_mapping[bank]:
                application_rate = bank_application_mapping[bank][application_type]
                tax_administrative = bank_application_mapping[bank]['tax_administrative']

                # Primeiro montante do mês
                first_month_money = (initial_application + contributions_monthly) * (1 + application_rate)

                # Total de contribuições ao longo dos anos (usando juros compostos anuais)
                contribution_total = first_month_money * ((1 + application_rate)**quantity_years - 1) / application_rate
                
                total_money = (initial_application + contribution_total) * (1 - tax_administrative)

                # Total gasto ao longo dos anos
                spent_total_per_years = total_money / (spent_monthly * monthly_per_year)
            
                return {
                    'first_month_money': first_month_money,
                    'contribution_total': contribution_total,
                    'total_money': total_money,
                    'spent_total_per_years': spent_total_per_years
                }
        else:
            monthly_per_year = 12
            today_date = date.today()
            current_year = today_date.year
            quantity_years = date_retireday - current_year

            bank_application_mapping = {
                'Itau': {'fixed_income': 12.30/100, 'variable_income': 14/100 , 'multi_market':15/100,'tax_administrative':0.95/100},
                'Santander': {'fixed_income': 12.50/100, 'variable_income': 13/100, 'multi_market': 14/100, 'tax_administrative': 0.99/100},
                'Bradesco': {'fixed_income': 12.85/100, 'variable_income': 12/100, 'multi_market': 13/100, 'tax_administrative': 0.98/100},
                'Banco_do_Brasil': {'fixed_income': 12/100, 'variable_income': 11/100, 'multi_market': 12/100, 'tax_administrative': 1/100}
            }

            if bank in bank_application_mapping and application_type in bank_application_mapping[bank]:
                application_rate = bank_application_mapping[bank][application_type]
                tax_administrative = bank_application_mapping[bank]['tax_administrative']

                # Primeiro montante do mês
                first_month_money = (initial_application + contributions_monthly) * (1 + application_rate)

                # Total de contribuições ao longo dos anos (usando juros compostos anuais)
                contribution_total = first_month_money * ((1 + application_rate)**quantity_years - 1) / application_rate
                
                total_money = (initial_application + contribution_total) * (1 - tax_administrative)

                # Total gasto ao longo dos anos
                spent_total_per_years = total_money / (spent_monthly * monthly_per_year)
            
                return {
                    'first_month_money': first_month_money,
                    'contribution_total': contribution_total,
                    'total_money': total_money,
                    'spent_total_per_years': spent_total_per_years
                }



            
            