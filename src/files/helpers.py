import json

import numpy as np
import pandas as pd
from django.shortcuts import get_object_or_404

from accounts.models import Company, CompanyDetailsIntegration
from files.models import CompanyFile, TransporterFile, TransporterFileResults
from reports.models import Report
from supplements.models import Supplement, TransporterImplementation, Weight, WeightPrices


def getting_supplements_transporters(company):
    """
    Getting supplements and transporters from company
    """
    supplements = Supplement.objects.filter(company=company)
    return [supplement.transporter.name for supplement in supplements]


def company_file_exists(report):
    """
    Check if company file exists in report database
    """
    return bool(CompanyFile.objects.filter(report=report).exists())


def transporter_file_exists(report, transporter):
    """
    Check if transporter file exists in report database
    """
    return bool(TransporterFile.objects.filter(report=report, transporter=transporter).exists())


def parse_file(file, extension, header_row):
    """Parses file and return it for analysis"""

    df = None

    if extension in ['.xls', '.xlsx']:
        df = pd.read_excel(file, skiprows=int(header_row))

    elif extension == ".xml":
        df = pd.read_xml(file)

    elif extension == ".csv":
        df = pd.read_csv(file, skiprows=int(header_row))

    return df.to_json()


def get_company_header_row(company):
    """
    Get header row from company details integration
    """
    company_integrations = CompanyDetailsIntegration.objects.get(company=company)
    return company_integrations.header_row


def get_transporter_header_row(supplement, transporter):
    """
    Get header row from transporter details integration
    """
    supplement = Supplement.objects.get(pk=supplement, transporter=transporter)
    supplement_details = TransporterImplementation.objects.get(supplement=supplement)

    return supplement_details.header_row


def analyze_company_file(pk, company):
    """
    Analyze company file
    """
    # Retrieving company data
    company_file = CompanyFile.objects.get(pk=pk)
    data = json.loads(company_file.data)
    df_company = pd.DataFrame(data)
    # Retrieving columns to keep
    company_details_integration = CompanyDetailsIntegration.objects.get(company=company)
    # Column date
    column_date = company_details_integration.column_date
    column_date = list(column_date.keys())
    column_date = ''.join(column_date)
    # Column weight
    column_weight = company_details_integration.column_weight
    column_weight = list(column_weight.keys())
    column_weight = ''.join(column_weight)
    # Column package number
    column_package_number = company_details_integration.column_package_number
    column_package_number = list(column_package_number.keys())
    column_package_number = ''.join(column_package_number)

    # Keeping columns
    columns_to_keep = [column_date, column_weight, column_package_number]
    cols = [col for col in df_company.columns if col in columns_to_keep]

    # Final DF
    df_company = df_company[cols]
    df = df_company[cols]
    df = df_company.dropna(subset=[column_date])

    # '''Handling weights'''


    return df_company.to_json()


def length_column_supplements(supplement):
    """
    Get length of column supplements
    """
    supplement = Supplement.objects.get(pk=supplement)
    transporter_implementation = TransporterImplementation.objects.get(supplement=supplement)
    column_supplements = transporter_implementation.columns_supplements
    column_supplements = list(column_supplements.keys())
    return len(column_supplements)


def parse_weights(company, transporter):
    """ Retrieves WEIGHTS from queryset and cleans data. """

    # Creating DF
    weight_id = Weight.objects.filter(company=company, transporter=transporter)
    query_weights = WeightPrices.objects.filter(weight__in=weight_id).values()
    df = pd.DataFrame(query_weights)

    # Processing columns
    weight_columns = Weight.objects.get(company=company, transporter=transporter)
    columns_to_keep = weight_columns.columns_to_keep
    columns_to_keep = list(columns_to_keep.keys())
    cols = [col for col in df.columns if col in columns_to_keep]

    # Final DF
    df = df[cols]

    print('ok')

    return df.to_dict()


def analyze_transporter_file(supplement, transporter, report):
    """
    The analyze_transporter_file function takes a supplement, a transporter and the report as arguments. It then
    """

    # Retrieving transporter data
    supplement = Supplement.objects.get(pk=supplement)
    transporter_file = TransporterFile.objects.get(report=report, transporter=transporter)
    data = json.loads(transporter_file.data)
    df_transporter = pd.DataFrame(data)

    # Get columns names from transporter implementation
    transporter_implementation = TransporterImplementation.objects.get(supplement=supplement)
    # Column price
    column_price = transporter_implementation.column_price
    column_price = list(column_price.keys())
    column_price = ''.join(column_price)
    # Column weight
    column_weight = transporter_implementation.column_weight
    column_weight = list(column_weight.keys())
    column_weight = ''.join(column_weight)
    # Column package number
    column_package_number = transporter_implementation.column_package_number
    column_package_number = list(column_package_number.keys())
    column_package_number = ''.join(column_package_number)
    # Column date
    column_date = transporter_implementation.column_date
    column_date = list(column_date.keys())
    column_date = ''.join(column_date)

    '''For the column supplements. We can have two choices : 1) The column is one column and is mixed with the 
        column "Prestation type". In this case, we'll have to exclude rows containing supplements and add them up to 
        the actual prices. 2) There are multiple columns that can be easily added up to the actual prices. '''

    # Column supplements
    column_supplements = transporter_implementation.columns_supplements
    column_supplements = list(column_supplements.keys())

    # Retrieving weights data
    # df_weights_data = parse_weights(company=report.company, transporter=transporter)
    # df_weights = pd.DataFrame(df_weights_data)

    if length_column_supplements(supplement=supplement.pk) == 1:
        column_supplements = ''.join(column_supplements)
        # Rows with supplements. Processing text
        df_transporter[column_supplements] = df_transporter[column_supplements].str.lower()
        df_transporter[column_supplements] = df_transporter[column_supplements].str.replace(' ', '_')
        df_transporter[column_supplements] = df_transporter[column_supplements].str.normalize('NFKD').str.encode(
            'ascii',
            errors='ignore').str.decode('utf-8')
        # Creating DF with supplements
        df_supplements = df_transporter[[column_package_number, column_supplements, column_price]]
        df_supplements = df_supplements[
            df_supplements[column_supplements].str.contains('supplement|surcharge|surete|supp|zone|frais')]
        df_supplements.rename(
            columns={column_price: column_price + "2", column_supplements: column_supplements + "2"},
            inplace=True)
        # Removing rows with supplements in original DF
        df_transporter = df_transporter[
            ~df_transporter[column_supplements].str.contains('supplement|surcharge|surete|supp|zone|frais')]
        # Adding up prices
        df = pd.merge(df_transporter, df_supplements, on=column_package_number, how='outer')
        df = df.fillna(0)
        df['Result'] = df[column_price] + df[column_price + "2"]

        # Registering results
        result_supplements = df_supplements[column_price + "2"].sum()
        result_total_prices = df['Result'].sum()

        return df.to_json(), df_supplements.to_json(), result_supplements, result_total_prices

    elif length_column_supplements(supplement=supplement.pk) > 1:

        ''' A CORRIGER '''


        # Rows with supplements. Processing text
        column_supplements = column_supplements
        df_supplements = df_transporter.copy()
        columns_to_keep = column_supplements
        columns_to_keep.append(column_package_number)
        cols = [col for col in df_supplements.columns if col in columns_to_keep]
        df_supplements = df_supplements[cols]
        df_supplements[column_supplements] = df_supplements[column_supplements].fillna(0)
        df_supplements['Total'] = df_supplements.sum(axis=1)

        #Registering results
        result_supplements = df_supplements['Total'].sum()
        result_total_prices = df_transporter[column_price].sum()
        print('Ok')

        return df_transporter.to_json(), df_supplements.to_json(), result_supplements, result_total_prices



def display_transporter_file_data(report):
    """
    The display_data_transporter_file function takes a transporter file as argument. It then
    """

    report = Report.objects.get(pk=report.pk)
    transporter_files = TransporterFile.objects.filter(report=report)
    list_results_supplements = []
    list_results_total_prices = []


    for transporter_file in transporter_files:
        transporter_file_profile = TransporterFile.objects.get(pk=transporter_file.pk)
        transporter_file_results = TransporterFileResults.objects.get(transporter_file=transporter_file_profile)
        list_results_supplements.append(transporter_file_results.result_supplements)
        list_results_total_prices.append(transporter_file_results.result_total_prices)


    total_results_supplements = sum(list_results_supplements)
    total_results_total_prices = sum(list_results_total_prices)

    return total_results_supplements, total_results_total_prices


