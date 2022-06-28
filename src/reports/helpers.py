import json
import zipfile
from io import BytesIO
from pprint import pprint

import numpy as np
import pandas as pd
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from accounts.models import Company, CompanyDetailsIntegration, Transporter
from files.helpers import parse_weights
from files.models import TransporterFile, TransporterFileResults, CompanyFile, CompanyFileResult
from reports.models import Report, ReportResults
from supplements.models import TransporterImplementation, Supplement


def assign_company_to_report(pk, user):
    """
    Assign a company to a report.
    If the user belongs to a brand, then the brand is also assigned.
    """

    report = Report.objects.get(pk=pk)
    report.company = user.company

    if user.company.brand:
        report.brand = user.company.brand


def display_chart_transporter(report):
    """
    Display transporter chart
    """
    report = Report.objects.get(pk=report.pk)
    report_details = ReportResults.objects.filter(report=report)
    list_transporter = []
    list_theorical_prices = []
    list_calculated_prices = []
    list_supplements = []
    list_discrepancies = []


    for item in report_details:
        # transporter_file_profile = TransporterFile.objects.get(pk=transporter_file.pk)
        # report_detail = ReportResults.objects.get(transporter_file=transporter_file.pk)
        list_transporter.append(item.transporter.name)
        list_theorical_prices.append(float(item.total_theorical_prices))
        list_calculated_prices.append(float(item.total_calculated_prices))
        list_supplements.append(float(item.total_supplements))
        list_discrepancies.append(float(item.total_discrepancies))


    return list_transporter, list_theorical_prices, list_calculated_prices, list_supplements, list_discrepancies


def transforming_dictionary_to_string(data):
    """
    Transform dictionary into string
    """
    d = list(data.keys())

    if len(d) == 1:
        ''.join(d)
    elif len(d) > 1:
        d = d

    return d


def columns_names_transporter(company, transporter):
    """
    Get columns names from transporter file
    """
    # Getting supplement to get columns names
    dict_columns_names_transporter = {}
    supplement = Supplement.objects.get(company=company, transporter=transporter)
    supplement_details = TransporterImplementation.objects.get(supplement=supplement)

    # Getting columns names and assigning to a dictionary
    dict_columns_names_transporter = {
        'column_price': transforming_dictionary_to_string(supplement_details.column_price),
        'column_package_number': transforming_dictionary_to_string(supplement_details.column_package_number),
        'column_prestation_type': transforming_dictionary_to_string(supplement_details.column_prestation_type),
        'column_weight': transforming_dictionary_to_string(supplement_details.column_weight),
        'columns_supplements': transforming_dictionary_to_string(supplement_details.columns_supplements),
        'column_date': transforming_dictionary_to_string(supplement_details.column_date),
    }

    return dict_columns_names_transporter


def columns_names_company(company):
    """
    Get columns names from company
    """
    # Getting company to get columns names
    dict_columns_names_company = {}
    company = get_object_or_404(Company, name=company)
    company_details_integration = CompanyDetailsIntegration.objects.get(company=company)

    # Getting columns names and assigning to a dictionary
    dict_columns_names_company = {
        'column_weight': transforming_dictionary_to_string(company_details_integration.column_weight),
        'column_package_number': transforming_dictionary_to_string(company_details_integration.column_package_number),
        'column_date': transforming_dictionary_to_string(company_details_integration.column_date)
    }

    return dict_columns_names_company


def get_company_file_data(report, company):
    """
    Get company file data (JSON Format)
    """
    company_file = get_object_or_404(CompanyFile, report=report, company=company)
    company_file_result = CompanyFileResult.objects.get(company_file=company_file.pk)
    company_data = company_file_result.result_comparison_company
    company_data = json.loads(company_data)

    return company_data


def get_transporter_file_data(report, transporter):
    """
    Get transporter file data (JSON Format)
    """
    transporter_file = get_object_or_404(TransporterFile, report=report, transporter=transporter)
    transporter_file_result = TransporterFileResults.objects.get(transporter_file=transporter_file.pk)
    transporter_data = transporter_file_result.result_comparison_transporter
    transporter_data = json.loads(transporter_data)

    return transporter_data

def get_company_supplements(company, transporter):
    """
    Get the list of supplements for a company and transporter
    """

    supplement_profile = Supplement.objects.get(company=company, transporter=transporter)
    return supplement_profile.supplements


def result_comparison(report, company, transporter):
    """
    The result_comparison function compares the results of a report with a company and a transporter.


    :param report: Get the report id
    :param company: Get the company name and its columns names
    :param transporter: Get the columns names for the transporter file
    :return: The dataframe with the comparison of the results from a report and a company
    :doc-author: Trelent
    """
    """
    The result_comparison function compares the results of a report with a company and a transporter.
    """

    ''' REPORT '''
    # Getting report
    report = Report.objects.get(pk=report.pk)

    ''' SUPPLEMENT '''
    # Getting supplement
    supplements = get_company_supplements(company, transporter)
    df_supplements = pd.DataFrame(supplements)
    df_supplements.rename(columns={'Supplement': 'Type_prestation2'}, inplace=True)
    df_supplements.insert(0, 'Type_prestation2', df_supplements.pop('Type_prestation2'))

    ''' TRANSPORTER FILE '''
    # Getting results from TransporterFile
    transporter_data = get_transporter_file_data(report, transporter)
    df_transporter = pd.DataFrame(transporter_data)

    # Getting transporter columns names
    transporter_columns_names = columns_names_transporter(company, transporter)
    # Transforming data
    transporter_column_price = transporter_columns_names['column_price']
    transporter_column_price = ''.join(transporter_column_price).replace(' ', '_')

    transporter_column_package_number = transporter_columns_names['column_package_number']
    #Transforming data
    transporter_column_prestation_type = transporter_columns_names['column_prestation_type']
    transporter_column_prestation_type = ''.join(transporter_column_prestation_type).replace(' ', '_')

    transporter_column_weight = transporter_columns_names['column_weight']
    transporter_columns_supplements = transporter_columns_names['columns_supplements']
    transporter_column_date = transporter_columns_names['column_date']

    ''' COMPANY FILE '''
    # Getting results from CompanyFile
    company_data = get_company_file_data(report, company)
    df_company = pd.DataFrame(company_data)

    # Getting company columns names
    company_columns_names = columns_names_company(company)
    company_column_weight = company_columns_names['column_weight']
    company_column_package_number = company_columns_names['column_package_number']
    company_column_date = company_columns_names['column_date']

    # Merging DFS
    df = df_transporter.merge(df_company, how='outer')
    df.columns = df.columns.str.replace(' ', '_')

    # Processing comparison
    df_weights_data = parse_weights(company=company, transporter=transporter)
    df_weights = pd.DataFrame(df_weights_data)
    weights_comparison = df['Poids'].values
    min_weights_comparison = df_weights['min_weight'].values
    max_weights_comparison = df_weights['max_weight'].values

    i, j = np.where((weights_comparison[:, None] >= min_weights_comparison) & (
            weights_comparison[:, None] <= max_weights_comparison))

    df2 = pd.concat([
        df.loc[i, :].reset_index(drop=True),
        df_weights.loc[j, :].reset_index(drop=True)], axis=1).append(
        df[~np.in1d(np.arange(len(df)), np.unique(i))],
        ignore_index=True, sort=False)

    df2.rename(columns={'price': 'Weight_price'}, inplace=True)
    df2['Weight_price'] = df2['Weight_price'].astype(float).fillna(0)
    df2['Supplement'] = df2.merge(df_supplements, how='left', on='Type_prestation2')['Price']
    df2['Supplement'] = df2['Supplement'].astype(float).fillna(0)
    df2['Final_price'] = df2['Weight_price'] + df2['Supplement']


    #FINAL PRICES

    total_theorical_prices = df2['Result'].sum()
    total_calculated_prices = df2['Final_price'].sum()
    total_supplements = df2['Supplement'].sum()
    total_discrepancies = total_theorical_prices - total_calculated_prices

    return df2.to_json(), total_theorical_prices, total_calculated_prices, total_supplements, total_discrepancies


def result_comparison_weight(report, company, transporter):
    """
    The result_comparison_weight function compares the weights of a report with a company and a transporter.
    """

    # Dropping columns
    columns_to_keep = []

    # Getting company names
    company_columns_names = columns_names_company(company)
    company_column_weight = company_columns_names['column_weight']
    company_column_weight = "".join(company_column_weight).replace(' ', '_')
    company_column_package_number = company_columns_names['column_package_number']
    company_column_package_number = "".join(company_column_package_number).replace(' ', '_')

    # Getting transporter names
    transporter_columns_names = columns_names_transporter(company, transporter)
    transporter_column_weight = transporter_columns_names['column_weight']
    transporter_column_weight = "".join(transporter_column_weight).replace(' ', '_')
    transporter_column_package_number = transporter_columns_names['column_package_number']
    transporter_column_package_number = "".join(transporter_column_package_number).replace(' ', '_')

    # Getting results
    report = get_object_or_404(Report, pk=report.pk)
    report_details = ReportResults.objects.get(report=report, transporter=transporter)
    comparison_data = report_details.result
    df = pd.read_json(comparison_data)

    # Processing comparison
    df['IsWeightSimilar'] = np.where(df[company_column_weight] == df[transporter_column_weight], 'Yes', 'No')

    # Dropping columns
    columns_to_keep.extend([transporter_column_package_number, transporter_column_weight, company_column_weight,
                            'IsWeightSimilar'])

    cols = [col for col in df.columns if col in columns_to_keep]
    df = df[cols]

    return df.to_json()


def get_transporters_list_with_files(report):
    """
    Get the list of transporters with their files
    """
    # Getting report
    transporter_list = []
    reports_details_transporter_list = []
    report = Report.objects.get(pk=report)
    reports_detail = ReportResults.objects.filter(report=report)
    for item in reports_detail:
        reports_details_transporter_list.append(item.transporter.name)
        print(reports_details_transporter_list)

    supplements_transporters = Supplement.objects.filter(company=report.company)
    for supplement in supplements_transporters:
        transporter = supplement.transporter.name
        if transporter in reports_details_transporter_list:
            transporter_list.append(transporter)

    return transporter_list


# def accessing_report_results(general_result_data, weight_data):
#     """
#     Download the results of a report
#     """
#     # Getting results
#
#     general_result_data = json.loads(general_result_data)
#     weight_data = json.loads(weight_data)
#
#     return general_result_data, weight_data


def create_downloadable_report(transporter, report, name):
    """
    Create a downloadable report
    """
    # Getting transporters

    transporter_list = get_transporters_list_with_files(report=report.pk)

    for transporter in transporter_list:

        reports_detail = get_object_or_404(ReportResults, report=report,
                                       transporter=get_object_or_404(Transporter, name=transporter))
        general_result_data = reports_detail.result
        weights_data = reports_detail.result_comparison_weights

        general_result_data = json.loads(general_result_data)
        df_general_result = pd.DataFrame(general_result_data)
        weight_data = json.loads(weights_data)
        df_weights = pd.DataFrame(weight_data)

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        with BytesIO() as b:
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            wb = writer.book
            # Sheet 1 - Report
            df_general_result.to_excel(writer, sheet_name='Report', index=False)
            ws = writer.sheets['Report']
            number_rows = len(df_general_result.index) + 1
            format1 = wb.add_format({'bg_color': '#FFC7CE',
                                     'font_color': '#9C0006'})

            # ws.conditional_format("$A$1:$O$%d" % (number_rows),
            #                       {"type": "formula",
            #                        "criteria": '=INDIRECT("O"&ROW())="No"',
            #                        "format": format1
            #                        }
            #                       )

            # Sheet 2 - Weights
            df_weights.to_excel(writer, sheet_name='Weights', index=False)
            number_rows = len(df_weights.index) + 1
            ws = writer.sheets['Weights']
            format1 = wb.add_format({'bg_color': '#FFC7CE',
                                     'font_color': '#9C0006'})

            writer.save()
            filename = "Report - " + name + ".xlsx"
            content_type = 'application/vnd.ms-excel'
            response = HttpResponse(b.getvalue(), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'

        return response


