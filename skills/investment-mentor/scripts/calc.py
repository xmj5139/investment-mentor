"""Optional deterministic arithmetic. Read JSON from stdin or a file; no network or writes.

Every amount must share a user-chosen currency/unit. Outputs validate arithmetic,
not source truth, account classification, complete deal rights or investment merit.
"""
import argparse
import json
import math
import sys
from pathlib import Path

def number(data,key):
    value=data.get(key)
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError(f'{key}: explicit finite number required')
    return float(value)

def ratio(data,key):
    value=number(data,key)
    if not 0<=value<=1:raise ValueError(f'{key}: must be in [0,1]')
    return value

def calculate(d):
    op=d.get('op')
    if op=='growth':
        base=number(d,'base');end=number(d,'end')
        if base<=0 or end<0:raise ValueError('Ordinary growth requires positive base and nonnegative end')
        result={'ratio':end/base,'growth_rate':end/base-1}
        if 'years' in d:
            years=number(d,'years')
            if years<=0:raise ValueError('years must be positive')
            result['cagr']=(end/base)**(1/years)-1
    elif op=='profit_check':
        revenue=number(d,'revenue');margin=ratio(d,'gross_margin')
        fees=sum(number(d,key) for key in ('research','admin','selling'))
        reported=number(d,'reported_pretax');simple=revenue*margin-fees
        result={'displayed_simple_result':simple,'reported_pretax':reported,'unexplained_difference':reported-simple,
                'scope':'Gross profit minus only the supplied expenses; not a complete accounting pretax result'}
        if 'margin_rounding_step' in d:
            step=number(d,'margin_rounding_step')
            if step<=0 or revenue<=0:raise ValueError('Positive rounding step and revenue required')
            low=max(0,margin-step/2);high=min(1,margin+step/2)
            result.update({'possible_simple_range':[revenue*low-fees,revenue*high-fees],
                           'implied_margin_if_no_other_items':(reported+fees)/revenue,
                           'rounding_note':'Approximate interval under round-to-nearest; actual rounding policy and omitted items remain unknown'})
    elif op=='cash_budget':
        current=number(d,'opening_available_cash');floor=number(d,'minimum_cash')
        periods=d.get('periods')
        if not isinstance(periods,list) or not periods:raise ValueError('periods: nonempty list required')
        lowest=current
        rows=[]
        for row in periods:
            opening=current
            current+=sum(number(row,k) for k in ('operating_net','investing_net','financing_net','other_net'))
            lowest=min(lowest,current)
            rows.append({'period':row.get('period'),'opening':opening,'closing':current,'below_minimum':current<floor})
        result={'periods':rows,'lowest_cash':lowest,'additional_cash_to_floor':max(0,floor-lowest),
                'scope':'Period-end available-cash budget; intraperiod payments and source classification not verified'}
    elif op=='exit_return':
        invested=number(d,'invested');equity=number(d,'exit_equity');stake=ratio(d,'stake')
        basis=d.get('stake_basis');years=number(d,'years');cost=number(d,'investor_cost_tax')
        if invested<=0 or equity<0 or years<=0 or cost<0:raise ValueError('Invalid amount/years')
        if basis=='current':stake*=ratio(d,'retention')
        elif basis=='exit':
            if 'retention' in d:raise ValueError('Exit fully diluted stake must not be diluted again; omit retention')
        else:raise ValueError('stake_basis must be current or exit')
        cash=equity*stake-cost
        if cash<0:raise ValueError('Net distribution negative; use full dated cash flows')
        result={'exit_stake':stake,'net_exit_cash':cash,'moic':cash/invested,
                'single_flow_irr':(cash/invested)**(1/years)-1,
                'assumptions':'Ordinary equal rights, one initial investment and one exit, no interim distributions or follow-on investment'}
    elif op=='price_limit':
        equity=number(d,'exit_equity');retention=ratio(d,'retention')
        if equity<0:raise ValueError('exit_equity must be nonnegative')
        limits={}
        if 'target_moic' in d:
            multiple=number(d,'target_moic')
            if multiple<=0:raise ValueError('target_moic must be positive')
            limits['moic_post_money_limit']=equity*retention/multiple
        if 'annual_return' in d:
            rate=number(d,'annual_return');years=number(d,'years')
            if rate<=-1 or years<=0:raise ValueError('Invalid annual return or years')
            limits['irr_post_money_limit']=equity*retention/(1+rate)**years
        if not limits:raise ValueError('At least one explicit return requirement is needed')
        result={**limits,'joint_post_money_limit':min(limits.values()),
                'scope':'Given scenario and return constraints only; not independently supported fair value; no extra duplicate discount'}
    elif op=='interval_divide':
        low=number(d,'low');high=number(d,'high');denom=number(d,'denominator')
        if low>high or denom<=0:raise ValueError('Ordered bounds and positive denominator required')
        result={'interval':[low/denom,high/denom],'qualifier':d.get('qualifier','inclusive')}
    else:raise ValueError('Unsupported op')
    return {'op':op,'result':result,'input_verified':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',nargs='?',type=Path)
    args=parser.parse_args()
    try:
        raw=args.input.read_text(encoding='utf-8-sig') if args.input else sys.stdin.read()
        data=json.loads(raw)
        if not isinstance(data,dict):raise ValueError('JSON object required')
        print(json.dumps(calculate(data),ensure_ascii=False,indent=2,allow_nan=False))
    except (ValueError,OSError) as exc:
        print(json.dumps({'error':str(exc),'input_verified':False},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(2)
