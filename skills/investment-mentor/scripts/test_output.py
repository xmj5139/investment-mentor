"""Tests of the optional mechanical checker, not tests of an agent/model."""
from pathlib import Path
import json,re
from decimal import Decimal
from check_output import check

ROOT=Path(__file__).resolve().parents[1]
def block(text,title):
 p=re.compile(r'(?ms)^## '+re.escape(title)+r'\n.*?(?=^## |^# |\Z)');m=p.search(text);assert m,title;return m
def replace_block(text,title,body):
 m=block(text,title);return text[:m.start()]+'## '+title+'\n\n'+body+'\n\n'+text[m.end():]
def drop_row(text,start):
 pattern=re.compile(r'(?m)^\| '+re.escape(start)+r' \|[^\n]*\n');new,count=pattern.subn('',text,count=1);assert count;return new
def run():
 s=json.loads((ROOT/'references/output-schema.json').read_text(encoding='utf-8'));fixtures=ROOT/'tests/fixtures'
 case=json.loads((fixtures/'anonymous-case.json').read_text(encoding='utf-8'));facts=case['facts'];budget=case['budget'];trade=case['scenario'];D=lambda x:Decimal(str(x))
 cash=D(budget['opening_available_cash']);cash_rows=[]
 for flow in budget['monthly_operating_net']:cash+=D(flow);cash_rows.append(cash)
 post=D(trade['pre_money'])+D(trade['all_new_cash']);stake=D(trade['investor_cash'])/post;exit_stake=stake*D(trade['retention_to_exit'])
 distributions=[D(trade['exit_equity_'+k])*exit_stake for k in ['base','down','up']];moics=[x/D(trade['investor_cash']) for x in distributions]
 assert cash_rows==[D(60),D(30)] and min(cash_rows)>=D(budget['minimum_cash'])
 assert post==D(2000) and stake==D('.1') and exit_stake==D('.08') and distributions==[D(400),D(120),D(560)] and moics==[D(2),D('.6'),D('2.8')]
 fcf=D(facts['operating_cash_2025'])-D(facts['cash_capex_2025']);assert fcf==D(100)
 sample_math={'unit':'万元','cash_endings':[float(x) for x in cash_rows],'post_money':float(post),'current_stake':float(stake),'exit_stake':float(exit_stake),'scenario_distributions':[float(x) for x in distributions],'scenario_moics':[float(x) for x in moics],'scenario_annual_returns':[float(x)**(1/trade['years'])-1 for x in moics],'analysis_fcf':float(fcf),'scope':'Independent arithmetic of author fixture; not real inputs or model behavior.'}
 samples={depth:(fixtures/f'report-{depth}.md').read_text(encoding='utf-8') for depth in s['depths']}
 d=samples['detailed'];tests=[]
 def add(name,text,expected,depth='detailed',task='project'):tests.append((name,text,expected,depth,task))
 for depth,text in samples.items():add(depth+'_complete',text,True,depth)
 numbered_meta=d
 for i,name in enumerate(s['metadata'],1):numbered_meta=numbered_meta.replace('**'+name+'：**',str(i)+'. **'+name+'：**',1)
 add('numbered_metadata_preserves_six_fields',numbered_meta,True)
 add('typographic_heading_spaces',d.replace('9个投资人视角总览','9 个投资人视角总览').replace('DP五层纵向验证结果','DP 五层纵向验证结果').replace('ESG情况与投资影响','ESG 情况与投资影响'),True)
 add('display_emphasis_preserves_labels',d.replace('| 投资人视角 |','| **投资人视角** |').replace('| 真问题 |','| **真问题** |'),True)
 add('missing_top_layer',d[:d.index('# 三、专家附录')],False)
 add('top_order_changed',d.replace('# 一、投资判断简报','# 临时层').replace('# 二、结构化项目画像','# 一、投资判断简报').replace('# 临时层','# 二、结构化项目画像'),False)
 add('missing_metadata_field',re.sub(r'(?m)^\*\*任务与研究范围：\*\*[^\n]*\n','',d),False)
 add('missing_brief_field',re.sub(r'(?m)^\*\*当前投资倾向：\*\*[^\n]*\n','',d),False)
 m=block(d,'6. 当前关键认知维度展开');add('missing_profile_section',d[:m.start()]+d[m.end():],False)
 first=block(d,'1. 企业定义与当前阶段');second=block(d,'2. 当前资本价值点与支撑条件')
 swapped=d[:first.start()]+second.group()+d[first.end():second.start()]+first.group()+d[second.end():]
 add('profile_order_changed',swapped,False)
 add('missing_view_row',drop_row(d,'真客户'),False)
 add('duplicate_view_row',d.replace('| 真问题 |','| 真客户 |',1),False)
 add('missing_dimension_row',drop_row(d,'长期演化空间'),False)
 add('dp_layer_missing',drop_row(d,'设备复购的持续价值 | 事实层'),False)
 add('dp_layer_duplicated',d.replace('| 设备复购的持续价值 | 事实层 |','| 设备复购的持续价值 | 机制层 |',1),False)
 add('placeholder_only_section',replace_block(d,'10. 当前核心风险与否决条件','待核。'),False)
 add('table_only_explanation',replace_block(d,'2. 当前资本价值点与支撑条件','| 项目 | 状态 |\n| --- | --- |\n| 复购 | 待核 |'),False)
 add('missing_appendix_section',d[:block(d,'8. 规则遵循与未完成检查').start()]+d[block(d,'8. 规则遵循与未完成检查').end():],False)
 add('wrong_declared_depth',d,False,'brief')
 add('wrong_evidence_header',d.replace('发布或数据日期','发布日期',1),False)
 waiver='本节资料不足。\n\n已知：只有企业整体愿景。\n\n缺口：尚未识别可核对的具体价值对象。\n\n影响：暂停五层结论，不影响列出取证安排。\n\n所需证据：具体产品、客户和交付记录，再选择验证对象。'
 add('explicit_dp_waiver',replace_block(d,'7. DP五层纵向验证结果',waiver),True)
 add('incomplete_waiver',replace_block(d,'7. DP五层纵向验证结果',waiver.replace('所需证据：具体产品、客户和交付记录，再选择验证对象。','')),False)
 # ESG mutations test the format contract only, not the truth of ESG judgments.
 numbered=d
 for i,name in enumerate(s['esg_sections'],1):numbered=numbered.replace('### '+name,'### 9.'+str(i)+' '+name,1)
 add('esg_hierarchical_numbering',numbered,True)
 add('brief_ascii_esg_labels',samples['brief'].replace('环境（E）','E：环境').replace('社会（S）','S：社会').replace('治理（G）','G：治理'),True,'brief')
 inherited=d;first=True
 for layer in s['dp']:
  if first:first=False;continue
  inherited=inherited.replace('| 设备复购的持续价值 | '+layer+' |','| 同上 | '+layer+' |',1)
 add('unambiguous_dp_same_as_above',inherited,True)
 add('dp_inheritance_without_prior',d.replace('| 设备复购的持续价值 | 事实层 |','| 同上 | 事实层 |',1),False)
 add('esg_section_removed',d.replace('## 9. ESG情况与投资影响','## 9. 临时ESG标题',1),False)
 add('esg_subheading_removed',d.replace('### 环境情况（E）','环境情况（E）',1),False)
 add('esg_subheadings_reordered',d.replace('### 环境情况（E）','### 临时项',1).replace('### 社会情况（S）','### 环境情况（E）',1).replace('### 临时项','### 社会情况（S）',1),False)
 add('esg_empty_subsection',re.sub(r'(?ms)(^### 治理情况（G）\n).*?(?=^### |^## )',r'\1\n待核。\n\n',d,count=1),False)
 add('brief_esg_removed',samples['brief'].replace('### ESG情况与投资影响','ESG情况与投资影响',1),False,'brief')
 add('brief_esg_missing_governance',samples['brief'].replace('治理','管理').replace('（G）',''),False,'brief')
 # A specialized brief uses the same outer layers and an explicit allowed body.
 for task,names in s['specialized'].items():
  sample=samples['brief'];a=sample.index('# 二、结构化项目画像');b=sample.index('# 三、专家附录')
  body='\n\n'.join('## '+str(i)+'. '+name+'\n\n本条仅验证专项目录的机械切换，不作为该专项的业务样稿或模型回答。' for i,name in enumerate(names,1))
  add(task+'_explicit_specialized',sample[:a]+'# 二、结构化项目画像\n\n'+body+'\n\n'+sample[b:],True,'brief',task)
 results=[]
 for name,text,expected,depth,task in tests:
  r=check(text,depth,task,s);results.append({'test':name,'expected_mechanical_pass':expected,'observed_mechanical_pass':r['mechanical_contract_pass'],'checker_test_passed':r['mechanical_contract_pass']==expected,'observed_errors':r['errors']})
 return {'kind':'unit tests of mechanical checker, not agent runs','tests':results,'tests_total':len(results),'tests_passed':sum(r['checker_test_passed'] for r in results),'all_checker_tests_passed':all(r['checker_test_passed'] for r in results),'author_fixture_arithmetic':sample_math,'limits':'Positive fixtures are author-constructed; this does not test model obedience, factual accuracy, prose fluency or investment quality.'}

if __name__=='__main__':
 result=run();print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['all_checker_tests_passed'] else 1)
