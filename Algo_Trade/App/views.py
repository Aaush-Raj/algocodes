import pandas as pd
from django.shortcuts import render
from django.shortcuts import HttpResponse
from .algo_codes import  print_header, set_header, nf_ul, nf_nearest, bnf_ul, bnf_nearest, nf_highestoi_CE, nf_highestoi_PE, bnf_highestoi_CE, bnf_highestoi_PE,NSE_live_data,nse_df

print(print_header("Nifty",nf_ul,nf_nearest))

# def home(request):
#     nifty_current_value = nf_ul
#     nifty_current_strike = nf_nearest
#     banknifty_current_value = bnf_ul
#     banknifty_current_strike = bnf_nearest
#     nifty_major_support = nf_highestoi_CE
#     nifty_major_resistance = nf_highestoi_PE
#     banknifty_major_support = bnf_highestoi_CE
#     banknifty_major_resistance = bnf_highestoi_PE
#     nse_live_data = pd.DataFrame(data=NSE_live_data)
#     live_data_table = nse_df.to_html()

#     context = {
#     'nifty_current_value':nifty_current_value,
#     'nf_nearest':nf_nearest,
#     'banknifty_current_value':banknifty_current_value,
#     'banknifty_current_strike':banknifty_current_strike,
#     'nifty_major_support':nifty_major_support,
#     'nifty_major_resistance':nifty_major_resistance,
#     'banknifty_major_support':banknifty_major_support,
#     'banknifty_major_resistance':banknifty_major_resistance,
#     'nse_live_data':nse_live_data,
#     'live_data_table':live_data_table,

    
#     }
#     return render(request,'App/base.html',context)

def live_data(request):
    live_data_table = nse_df.to_html()
    return HttpResponse(live_data_table)

def main_page(request):
    return render(request,'App/home.html')

def nifty_data(request):
    nifty_current_value = nf_ul
    nifty_current_strike = nf_nearest
    banknifty_current_value = bnf_ul
    banknifty_current_strike = bnf_nearest
    nifty_major_support = nf_highestoi_CE
    nifty_major_resistance = nf_highestoi_PE
    banknifty_major_support = bnf_highestoi_CE
    banknifty_major_resistance = bnf_highestoi_PE
    nse_live_data = pd.DataFrame(data=NSE_live_data)
    live_data_table = nse_df.to_html()

    context = {
    'nifty_current_value':nifty_current_value,
    'nf_nearest':nf_nearest,
    'banknifty_current_value':banknifty_current_value,
    'banknifty_current_strike':banknifty_current_strike,
    'nifty_major_support':nifty_major_support,
    'nifty_major_resistance':nifty_major_resistance,
    'banknifty_major_support':banknifty_major_support,
    'banknifty_major_resistance':banknifty_major_resistance,
    'nse_live_data':nse_live_data,
    'live_data_table':live_data_table,

    
    }
    return render(request,'App/nifty_data.html',context)

def banknifty_data(request):
    nifty_current_value = nf_ul
    nifty_current_strike = nf_nearest
    banknifty_current_value = bnf_ul
    banknifty_current_strike = bnf_nearest
    nifty_major_support = nf_highestoi_CE
    nifty_major_resistance = nf_highestoi_PE
    banknifty_major_support = bnf_highestoi_CE
    banknifty_major_resistance = bnf_highestoi_PE
    nse_live_data = pd.DataFrame(data=NSE_live_data)
    live_data_table = nse_df.to_html()

    context = {
    'nifty_current_value':nifty_current_value,
    'nf_nearest':nf_nearest,
    'banknifty_current_value':banknifty_current_value,
    'banknifty_current_strike':banknifty_current_strike,
    'nifty_major_support':nifty_major_support,
    'nifty_major_resistance':nifty_major_resistance,
    'banknifty_major_support':banknifty_major_support,
    'banknifty_major_resistance':banknifty_major_resistance,
    'nse_live_data':nse_live_data,
    'live_data_table':live_data_table,

    
    }
    return render(request,'App/banknifty_data.html',context)