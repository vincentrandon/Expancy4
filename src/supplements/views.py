from django.shortcuts import render, redirect

# Create your views here.
from supplements.forms import SupplementForm
from supplements.models import Supplement


def see_supplements_per_company(request):
    supplements = Supplement.objects.filter(company=request.user.company)
    print(supplements)
    return render(request, 'transporters/transporters.html', context={'supplements': supplements})

def edit_transporter(request, slug):

    form = SupplementForm(request.POST or None, instance=Supplement.objects.get(slug=slug))

    if form.is_valid():
        form.save()
        return redirect('tool:transporters')

    return render(request, 'transporters/edit-transporter.html', context={'form': form})

