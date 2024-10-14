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
                            date_retireday, spent_monthly, application_type, method, validate_bank):
        try:
            
            
            # Verifica se a renda aplicável mensal é menor ou igual a limit_total_income
            if validate_bank == True:
                """
                Calcula a renda máxima aplicável mensal. 
                Ao qual limit_total_income é o resultado do calculo entre brute_income que é (a renda bruta atual) multiplicado por
                12 (meses) , multiplicado por 12% e por fim dividio por 12 meses resultando quanto é o máximo possível para investir por mês.
                """
                limit_total_income = ((brute_income * 12) * 12 / 100) / 12

                if limit_total_income <= contributions_monthly and method == "PGBL":
                    # Define o número de meses por ano
                    monthlys_per_year = 12

                    # Obtém a data de hoje e o ano atual
                    today_date = date.today()
                    current_year = today_date.year

                    # Calcula a quantidade de anos até a aposentadoria
                    quantity_years = date_retireday - current_year
                    
                    # Calcula a quantidade de meses até a aposentadoria
                    quantity_months = quantity_years * monthlys_per_year

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

                    try:
                        # Inicializa o primeiro mês do montante
                        total_amount = initial_application + contributions_monthly

                        # Aplica o rendimento do primeiro mês antes de entrar no loop
                        total_amount += total_amount * selected_application_type  # Aplica os juros do primeiro mês
                        total_amount -= total_amount * tax_administrative  # Aplica a taxa administrativa do primeiro mês

                        # Loop para calcular o montante ao longo dos meses com aportes mensais e juros
                        for i in range(1, quantity_months):  # Começa a partir do segundo mês
                            # Adiciona o aporte mensal (a partir do segundo mês)
                            total_amount += contributions_monthly
                            # Aplica os juros sobre o montante acumulado
                            total_amount += total_amount * selected_application_type
                            # Aplica a taxa administrativa sobre o montante acumulado
                            total_amount -= total_amount * tax_administrative

                            # No segundo mês, retorna o montante acumulado (com rendimento do primeiro mês)
                            if i == 1:
                                second_month_money = total_amount

                        # Calcula o total gasto ao longo dos anos
                        spent_total_per_years = total_amount / (spent_monthly * monthlys_per_year)

                    except TypeError:
                        flash("Erro: Tipo de dado incorreto encontrado durante o cálculo.", category='error')
                    except Exception as e:
                        flash(f"Ocorreu um erro inesperado: {e}", category='error')

                    result = {
                        'second_month_money': second_month_money,
                        'total_amount': total_amount,
                        'spent_total_per_years': spent_total_per_years
                    }
                    print(f"REsult com BAnk PGBL{result}")
                    return result
                    
                else:
                    # Define o número de meses por ano
                    monthlys_per_year = 12

                    # Obtém a data de hoje e o ano atual
                    today_date = date.today()
                    current_year = today_date.year

                    # Calcula a quantidade de anos até a aposentadoria
                    quantity_years = date_retireday - current_year
                    
                    # Calcula a quantidade de meses até a aposentadoria
                    quantity_months = quantity_years * monthlys_per_year

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

                    try:
                        # Inicializa o primeiro mês do montante
                        total_amount = initial_application + contributions_monthly

                        # Aplica o rendimento do primeiro mês antes de entrar no loop
                        total_amount += total_amount * selected_application_type  # Aplica os juros do primeiro mês
                        total_amount -= total_amount * tax_administrative  # Aplica a taxa administrativa do primeiro mês

                        # Loop para calcular o montante ao longo dos meses com aportes mensais e juros
                        for i in range(1, quantity_months):  # Começa a partir do segundo mês
                            # Adiciona o aporte mensal (a partir do segundo mês)
                            total_amount += contributions_monthly
                            # Aplica os juros sobre o montante acumulado
                            total_amount += total_amount * selected_application_type
                            # Aplica a taxa administrativa sobre o montante acumulado
                            total_amount -= total_amount * tax_administrative

                            # No segundo mês, retorna o montante acumulado (com rendimento do primeiro mês)
                            if i == 1:
                                second_month_money = total_amount

                        # Calcula o total gasto ao longo dos anos
                        spent_total_per_years = total_amount / (spent_monthly * monthlys_per_year)

                    except TypeError:
                        flash("Erro: Tipo de dado incorreto encontrado durante o cálculo.", category='error')
                    except Exception as e:
                        flash(f"Ocorreu um erro inesperado: {e}", category='error')


                    result = {
                        'second_month_money': second_month_money,
                        'total_amount': total_amount,
                        'spent_total_per_years': spent_total_per_years
                    }
                    print(f"REsult com BAnk VGBL{result}")
                    return result
            else:
                # Define o número de meses por ano
                monthlys_per_year = 12

                # Obtém a data de hoje e o ano atual
                today_date = date.today()
                current_year = today_date.year

                # Calcula a quantidade de anos até a aposentadoria
                quantity_years = date_retireday - current_year
                
                # Calcula a quantidade de meses até a aposentadoria
                quantity_months = quantity_years * monthlys_per_year

                """
                Como a opção bank não foi marcada ou seja False, não existe a taxa administrativa
                fixed_income é Renda fixa,
                variable_income é Renda Variável 
                multi_market é Mercado de ações
                
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

                try:
                    # Inicializa o primeiro mês do montante
                    total_amount = initial_application + contributions_monthly

                    # Aplica o rendimento do primeiro mês antes de entrar no loop
                    total_amount += total_amount * selected_application_type  # Aplica os juros do primeiro mês
                    total_amount -= total_amount * tax_administrative  # Aplica a taxa administrativa do primeiro mês

                    # Loop para calcular o montante ao longo dos meses com aportes mensais e juros
                    for i in range(1, quantity_months):  # Começa a partir do segundo mês
                        # Adiciona o aporte mensal (a partir do segundo mês)
                        total_amount += contributions_monthly
                        # Aplica os juros sobre o montante acumulado
                        total_amount += total_amount * selected_application_type
                        # Aplica a taxa administrativa sobre o montante acumulado
                        total_amount -= total_amount * tax_administrative

                        # No segundo mês, retorna o montante acumulado (com rendimento do primeiro mês)
                        if i == 1:
                            second_month_money = total_amount

                    # Calcula o total gasto ao longo dos anos
                    spent_total_per_years = total_amount / (spent_monthly * monthlys_per_year)

                except TypeError:
                    flash("Erro: Tipo de dado incorreto encontrado durante o cálculo.", category='error')
                except Exception as e:
                    flash(f"Ocorreu um erro inesperado: {e}", category='error')


                result = {
                    'second_month_money': second_month_money,
                    'total_amount': total_amount,
                    'spent_total_per_years': spent_total_per_years
                }
                print(f"REsult sem BAnk{result}")
                return result

        except KeyError as ke:
            return {'error': f'Erro de chave no mapeamento: {ke}'}
        except ValueError as ve:
            return {'error': f'Erro de valor: {ve}'}
        except TypeError as te:
            return {'error': f'Erro de tipo de dado: {te}'}
        except Exception as e:
            return {'error': f'Ocorreu um erro inesperado: {e}'}