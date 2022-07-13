import calendar
import os

from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from accounts.models import Transporter, CompanyDetailsIntegration
from files.forms import CompanyFileForm, TransporterFileForm, DeleteCompanyFileForm, DeleteTransporterFileForm
from files.helpers import getting_supplements_transporters, company_file_exists, parse_file, get_company_header_row, \
    get_transporter_header_row, transporter_file_exists, analyze_company_file, analyze_transporter_file, \
    display_transporter_file_data
from files.models import TransporterFile, CompanyFile, CompanyFileResult, TransporterFileResults
from reports.forms import ReportForm
from reports.helpers import display_chart_transporter, result_comparison, result_comparison_weight, \
    get_transporters_list_with_files, create_downloadable_report
from reports.models import Report, ReportResults
from supplements.models import Supplement


def create_report(request):
    form = ReportForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            obj = form.save(commit=False)

            # Assign company and brand
            obj.company = request.user.company
            if request.user.brand:
                obj.brand = request.user.brand

            # Assigning date to the report
            cd = form.cleaned_data
            filtered_date = cd.get('date')
            month = filtered_date.month
            month = calendar.month_name[month]
            year = filtered_date.year
            date_f = f"{str(month)} {str(year)}"
            obj.title = f"{obj.title} {date_f}"
            obj.save()

            return redirect('tool:single-report', slug=obj.slug)

        else:
            form = ReportForm()

    return render(request, 'reports/create-report.html', context={'form': form})


def display_all_reports(request):
    reports = Report.objects.filter(company=request.user.company)
    nb_reports = Report.objects.filter(company=request.user.company).count()
    return render(request, 'reports/reports.html', context={'reports': reports, 'nb_reports': nb_reports})


def display_single_report(request, slug):
    report = get_object_or_404(Report, slug=slug)
    request.session['report'] = report.pk
    request.session['slug'] = slug
    company_form = CompanyFileForm(instance=report)
    company_header_row = get_company_header_row(company=request.user.company)
    transporter_form = TransporterFileForm(instance=report)
    transporters = getting_supplements_transporters(request.user.company)
    missing_transporters = []
    list_c_transporters_avatars = []
    # Displaying results
    result_supplements = display_transporter_file_data(report=report)[0]
    result_total_prices = display_transporter_file_data(report=report)[1]

    ''' DISPLAYING CHARTS '''
    # Displaying chart of transporter costs
    chart_transporters = display_chart_transporter(report=report)[0]
    n_theorical_costs = display_chart_transporter(report=report)[1]
    n_total_calculated_costs = display_chart_transporter(report=report)[2]
    n_total_supplements = display_chart_transporter(report=report)[3]
    n_total_discrepancies = display_chart_transporter(report=report)[4]

    # Summing lists
    theorical_costs = sum(n_theorical_costs)
    total_calculated_costs = sum(n_total_calculated_costs)
    total_supplements = sum(n_total_supplements)
    total_discrepancies = sum(n_total_discrepancies)

    ''' Check if company file exists in report database '''
    check_company_file = company_file_exists(report)
    if company_file_exists(report):
        company_file = get_object_or_404(CompanyFile, report=report)
        company_file_form = DeleteCompanyFileForm(instance=company_file)
    else:
        company_file = None
        company_file_form = None

    ''' Check if transporter file exists in report database '''
    # If transporter does not appear in the list of transporters, it is added to the list of missing transporters.
    for transporter in transporters:
        transporter_id = get_object_or_404(Transporter, name=transporter)
        transporter_avatar = transporter_id.avatar_file_to_upload.url
        if not TransporterFile.objects.filter(report=report, transporter=transporter_id).exists():
            missing_transporters.append(transporter)


            transporter_file_form = TransporterFileForm()
        else:
            transporter_file = None
            transporter_file_form = None

    print(missing_transporters)

    if request.method == 'POST':
        print(request.POST)
        ''' COMPANY FILE '''
        ''' Block to delete company file '''

        if 'delete_company_file' in request.POST:
            company_file_form = DeleteCompanyFileForm(request.POST, request.FILES, instance=company_file)
            if company_file_form.is_valid():
                company_file.delete()
                return redirect('tool:single-report', slug=report.slug)

        ''' Block to create company file '''

        if 'company_form' in request.POST:
            company_form = CompanyFileForm(request.POST, request.FILES)
            if company_form.is_valid():
                obj = company_form.save(commit=False)
                company_form.save()
                # Updating fields
                obj.report = report
                obj.user = request.user
                obj.company = request.user.company
                obj.header_row = company_header_row
                obj.data = parse_file(file=obj.file, extension=os.path.splitext(obj.file.name)[1],
                                      header_row=company_header_row)
                obj.save()

                # Updating Company File Results
                company_result = analyze_company_file(pk=obj.pk, company=request.user.company)
                CompanyFileResult.objects.get_or_create(company_file=get_object_or_404(CompanyFile, pk=obj.pk),
                                                        result_comparison_company=company_result)
                obj.save()

                return redirect('tool:single-report', slug=slug)

            else:
                company_form = CompanyFileForm()
                return redirect('tool:single-report', slug=slug)

    ''' TRANSPORTER FILE '''
    ''' Block to delete transporter file '''

    if 'delete_transporter_file' in request.POST:
        transporter_name = request.POST.get('transporter_name')
        transporter_profile = get_object_or_404(Transporter, name=transporter_name)
        transporter_file = get_object_or_404(TransporterFile, report=report, transporter=transporter_profile)
        transporter_file_form = DeleteTransporterFileForm(request.POST, request.FILES, instance=transporter_file)
        report_details_transporter = get_object_or_404(ReportResults, report=report,
                                                       transporter=transporter_profile)

        if transporter_file_form.is_valid():
            transporter_file.delete()
            report_details_transporter.delete()
            return redirect('tool:single-report', slug=report.slug)

        ''' Block to create transporter file '''
    if 'transporter_form' in request.POST:
        transporter_form = TransporterFileForm(request.POST, request.FILES)

        if transporter_form.is_valid():

            if not company_file_exists(report):
                raise Http404('Company file is not uploaded')

            obj = transporter_form.save()
            # Updating fields
            transporter_name = get_object_or_404(Transporter, name=request.POST.get('transporter_name'))

            supplement = Supplement.objects.get(company=request.user.company, transporter=transporter_name)
            transporter_header_row = get_transporter_header_row(supplement=supplement.pk,
                                                                transporter=transporter_name)
            transporter_avatar_to_upload = transporter_name.avatar_file_to_upload
            transporter_avatar_uploaded = transporter_name.avatar_file_uploaded

            obj.transporter = transporter_name
            obj.company = request.user.company
            obj.report = report
            obj.user = request.user
            obj.data = parse_file(file=obj.file, extension=os.path.splitext(obj.file.name)[1],
                                  header_row=transporter_header_row)

            obj.save()

            # Updating Transporter File Results
            transporter_result = analyze_transporter_file(supplement=supplement.pk,
                                                          transporter=supplement.transporter, report=report)
            transporter_file_results = TransporterFileResults.objects.get_or_create(
                transporter_file=get_object_or_404(TransporterFile, pk=obj.pk),
                result_comparison_transporter=transporter_result[0],
                result_comparison_supplements=transporter_result[1],
                result_supplements=transporter_result[2], result_total_prices=transporter_result[3])



            ''' Block to update REPORT with results '''
            # Updating report with results

            comparison_results = result_comparison(report=report, company=request.user.company,
                                                   transporter=supplement.transporter)
            report_results = ReportResults.objects.get_or_create(report=report, transporter=supplement.transporter,
                                                                 result=comparison_results[0],
                                                                 total_theorical_prices=comparison_results[1],
                                                                 total_calculated_prices=comparison_results[2],
                                                                 total_supplements=comparison_results[3],
                                                                 total_discrepancies=comparison_results[4])
            comparison_results_weights = result_comparison_weight(report=report, company=request.user.company,
                                                                  transporter=supplement.transporter)
            report_results = ReportResults.objects.filter(report=report, transporter=supplement.transporter).update(
                result_comparison_weights=comparison_results_weights)

            return redirect('tool:single-report', slug=slug)

        else:
            transporter_form = TransporterFileForm()

    return render(request, 'reports/single-report.html',
                  context={'transporter_form': transporter_form, 'company_form': company_form,
                           'transporters': transporters, 'company_file_delete_form': company_file_form,
                           'check_company_file': check_company_file, 'missing_transporters': missing_transporters,
                           'result_supplements': result_supplements,
                           'transporter_file_delete_form': DeleteTransporterFileForm(),
                           'result_total_prices': result_total_prices, 'chart_transporters': chart_transporters,
                           'n_theorical_costs': n_theorical_costs, 'n_total_calculated_costs': n_total_calculated_costs,
                           'n_total_supplements': n_total_supplements, 'n_total_discrepancies': n_total_discrepancies,
                           'theorical_costs': theorical_costs, 'total_calculated_costs': total_calculated_costs,
                           'total_supplements': total_supplements, 'total_discrepancies': total_discrepancies,
                           'list_c_transporters_avatars': list_c_transporters_avatars}
                  )


def display_chart_transporter_costs(request):
    report_id = request.session['report']
    report = get_object_or_404(Report, pk=report_id)
    transporters = display_chart_transporter(report=report)[0]
    supplement_costs = display_chart_transporter(report=report)[1]
    total_costs = display_chart_transporter(report=report)[2]
    return render(request, 'charts/partial-chart-transporters-costs.html',
                  context={'transporters': transporters,
                           'supplement_costs': supplement_costs,
                           'total_costs': total_costs})


def download_report(request):
    report = get_object_or_404(Report, slug=request.session['slug'])
    transporter_list = get_transporters_list_with_files(report=report.pk)

    if request.method == 'GET':
        for transporter in transporter_list:
            reports_detail = get_object_or_404(ReportResults, report=report,
                                               transporter=get_object_or_404(Transporter, name=transporter))
            general_result_data = reports_detail.result
            weights_data = reports_detail.result_comparison_weights
            response = create_downloadable_report(general_result_data=general_result_data,
                                                  weight_data=weights_data, name=transporter)

            return response

# def get_partial_company_file(request):
#     report = get_object_or_404(Report, slug=request.session['slug'])
#     company_form = CompanyFileForm(instance=report)
#     company_file = get_object_or_404(CompanyFile, report=report)
#     company_header_row = get_company_header_row(company=request.user.company)
#
#     ''' Check if company file exists in report database '''
#     check_company_file = company_file_exists(report)
#     if company_file_exists(report):
#         company_file = get_object_or_404(CompanyFile, report=report)
#         company_file_form = DeleteCompanyFileForm(instance=company_file)
#     else:
#         company_file = None
#         company_file_form = None
#
#     ''' Block to delete company file '''
#
#     if request.method == 'POST':
#         print(request.POST)
#         if 'delete_company_file' in request.POST:
#             company_file_form = DeleteCompanyFileForm(request.POST, request.FILES, instance=company_file)
#             if company_file_form.is_valid():
#                 company_file.delete()
#                 return redirect('tool:single-report', slug=report.slug)
#
#         ''' Block to create company file '''
#
#         if 'company_form' in request.POST:
#             company_form = CompanyFileForm(request.POST, request.FILES)
#             if company_form.is_valid():
#                 obj = company_form.save(commit=False)
#                 company_form.save()
#                 # Updating fields
#                 obj.report = report
#                 obj.user = request.user
#                 obj.company = request.user.company
#                 obj.header_row = company_header_row
#                 obj.data = parse_file(file=obj.file, extension=os.path.splitext(obj.file.name)[1],
#                                       header_row=company_header_row)
#                 obj.save()
#
#                 # Updating Company File Results
#                 company_result = analyze_company_file(pk=obj.pk, company=request.user.company)
#                 CompanyFileResult.objects.get_or_create(company_file=get_object_or_404(CompanyFile, pk=obj.pk),
#                                                         result_comparison_company=company_result)
#                 obj.save()
#
#                 return redirect('tool:single-report', slug=request.session['slug'])
#
#     return render(request, 'reports/single-report/partial-company-file.html',
#                   context={'company_file_form': company_file_form, 'company_form': company_form,
#                            'check_company_file': check_company_file})
#
#
# def get_partial_transporter_files(request):
#     report = get_object_or_404(Report, slug=request.session['slug'])
#     transporter_list = get_transporters_list_with_files(report=report.pk)
#     transporter_form = TransporterFileForm(instance=report)
#     transporters = getting_supplements_transporters(request.user.company)
#     missing_transporters = []
#
#     ''' Block to get transporters '''
#
#     for transporter in transporters:
#         transporter_id = get_object_or_404(Transporter, name=transporter)
#         if not TransporterFile.objects.filter(report=report, transporter=transporter_id).exists():
#             missing_transporters.append(transporter)
#             transporter_file_form = TransporterFileForm()
#         else:
#             transporter_file = None
#             transporter_file_form = None
#
#     if request.method == 'POST':
#         ''' Block to delete transporter file '''
#
#         if 'delete_transporter_file' in request.POST:
#             transporter_name = request.POST.get('transporter_name')
#             transporter_profile = get_object_or_404(Transporter, name=transporter_name)
#             transporter_file = get_object_or_404(TransporterFile, report=report, transporter=transporter_profile)
#             transporter_file_form = DeleteTransporterFileForm(request.POST, request.FILES,
#                                                               instance=transporter_file)
#             report_details_transporter = get_object_or_404(ReportResults, report=report,
#                                                            transporter=transporter_profile)
#
#             if transporter_file_form.is_valid():
#                 transporter_file.delete()
#                 report_details_transporter.delete()
#                 return redirect('tool:single-report', slug=report.slug)
#
#         ''' Block to create transporter file '''
#
#         if 'transporter_form' in request.POST:
#             transporter_form = TransporterFileForm(request.POST, request.FILES)
#             if transporter_form.is_valid():
#
#                 if not company_file_exists(report):
#                     raise Http404('Company file is not uploaded')
#
#                 obj = transporter_form.save()
#                 # Updating fields
#                 transporter_name = get_object_or_404(Transporter, name=request.POST.get('transporter_name'))
#                 supplement = Supplement.objects.get(company=request.user.company, transporter=transporter_name)
#                 transporter_header_row = get_transporter_header_row(supplement=supplement.pk,
#                                                                     transporter=transporter_name)
#                 obj.transporter = transporter_name
#                 obj.company = request.user.company
#                 obj.report = report
#                 obj.user = request.user
#                 obj.data = parse_file(file=obj.file, extension=os.path.splitext(obj.file.name)[1],
#                                       header_row=transporter_header_row)
#
#                 obj.save()
#
#                 # Updating Transporter File Results
#                 transporter_result = analyze_transporter_file(supplement=supplement.pk,
#                                                               transporter=supplement.transporter, report=report)
#                 transporter_file_results = TransporterFileResults.objects.get_or_create(
#                     transporter_file=get_object_or_404(TransporterFile, pk=obj.pk),
#                     result_comparison_transporter=transporter_result[0],
#                     result_comparison_supplements=transporter_result[1],
#                     result_supplements=transporter_result[2], result_total_prices=transporter_result[3])
#
#                 ''' Block to update REPORT with results '''
#                 # Updating report with results
#
#                 comparison_results = result_comparison(report=report, company=request.user.company,
#                                                        transporter=supplement.transporter)
#                 report_results = ReportResults.objects.get_or_create(report=report,
#                                                                      transporter=supplement.transporter,
#                                                                      result=comparison_results[0],
#                                                                      total_theorical_prices=comparison_results[1],
#                                                                      total_calculated_prices=comparison_results[2],
#                                                                      total_supplements=comparison_results[3],
#                                                                      total_discrepancies=comparison_results[4])
#                 comparison_results_weights = result_comparison_weight(report=report, company=request.user.company,
#                                                                       transporter=supplement.transporter)
#                 report_results = ReportResults.objects.filter(report=report,
#                                                               transporter=supplement.transporter).update(
#                     result_comparison_weights=comparison_results_weights)
#
#                 return redirect('tool:single-report', slug=request.session['slug'])
#
#             else:
#                 transporter_form = TransporterFileForm()
#
#     return render(request, 'reports/single-report/partial-transporter-files.html',
#                   context={'transporter_form': transporter_form,
#                            'transporters': transporters,
#                            'missing_transporters': missing_transporters,
#                            'transporter_file_form': transporter_file_form})
