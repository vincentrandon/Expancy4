from django.shortcuts import render

# Create your views here.

''' INDEX WEBPAGE '''
def index(request):
    return render(request, 'tool/index.html')



