from django.http import HttpResponse

from .helpers import cli_account_list

def index(request):
    accounts = cli_account_list()
    return HttpResponse(str(accounts))
