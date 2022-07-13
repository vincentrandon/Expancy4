from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.shortcuts import render
from channels.layers import get_channel_layer

# Create your views here.

'''Get user infos'''



''' INDEX WEBPAGE '''
def index(request):
    return render(request, 'tool/index.html')

def testdesign(request):
    return render(request, 'tool/testdesign.html')
