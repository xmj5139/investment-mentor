"""Optional Markdown structure checker. Never grades facts, prose quality or investment merit."""
from pathlib import Path
import argparse,json,re
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[1]
def normalize(title):
 value=re.sub(r'^(?:[一二三四五六七八九十零]+[、.．]\s*|[0-9]+(?:\.[0-9]+)*[、.．)]?\s+)','',title.strip())
 return re.sub(r'\s+','',value)
def clean_code(text):
 lines=[];fence=False
 for line in text.splitlines():
  if re.match(r'^\s*(```|~~~)',line):fence=not fence;lines.append('');continue
  lines.append('' if fence else line)
 return lines
def payload(lines):
 values=[]
 for line in lines:
  v=line.strip().replace('**','')
  if not v or re.match(r'^#{1,6}\s',v) or re.fullmatch(r'[-:|\s]+',v):continue
  values.append(v)
 return '\n'.join(values)
def has_content(lines):
 v=payload(lines)
 return bool(v and not re.fullmatch(r'(?:TODO|待核|待补|未知|暂无|不适用|同上|见前文|省略|略)[。.!\s]*',v,re.I))
def narrative(lines):
 return any(re.search(r'[。！？.!?]',line) for line in lines if line.strip() and not line.lstrip().startswith(('|','#')))
def tables(lines):
 found=[];i=0
 def cell(value):return value.strip().replace('**','').replace('`','')
 while i+1<len(lines):
  if lines[i].strip().startswith('|') and re.fullmatch(r'[|:\-\s]+',lines[i+1].strip()):
   rows=[];j=i+2
   while j<len(lines) and lines[j].strip().startswith('|'):
    rows.append([cell(x) for x in lines[j].strip().strip('|').split('|')]);j+=1
   found.append(([cell(x) for x in lines[i].strip().strip('|').split('|')],rows));i=j
  else:i+=1
 return found
def check(text,depth='detailed',task='project',schema=None):
 s=schema or json.loads((ROOT/'references/output-schema.json').read_text(encoding='utf-8'))
 if depth not in s['depths'] or task not in ['project',*s['specialized']]:raise ValueError('Unknown depth/task')
 lines=clean_code(text);head=[];errors=[];waivers=[]
 for i,line in enumerate(lines):
  m=re.match(r'^(#{1,6})\s+(.+?)\s*#*$',line)
  if m:head.append((i,len(m[1]),normalize(m[2])))
 def section(start,level):
  end=next((i for i,l,_ in head if i>start and l<=level),len(lines));return lines[start+1:end]
 tops=[h for h in head if h[1]==1];expected=[normalize(x) for x in s['top']]
 if [h[2] for h in tops]!=expected:errors.append('一级标题缺失、增添或顺序不符')
 blocks={name:section(i,1) for i,l,name in tops}
 def fields(block,names,label):
  block=[re.sub(r'^\s*[0-9]+[.、)]\s+','',line) for line in block]
  positions=[]
  for name in names:
   hits=[i for i,line in enumerate(block) if re.match(r'^\s*'+re.escape(name)+r'\s*[:：]',line.replace('**',''))]
   if len(hits)!=1:errors.append(label+'字段缺失或重复：'+name);continue
   pos=hits[0];positions.append(pos)
   stop=next((j for j in range(pos+1,len(block)) if any(re.match(r'^\s*'+re.escape(x)+r'\s*[:：]',block[j].replace('**','')) for x in names)),len(block))
   value=re.sub(r'^\s*'+re.escape(name)+r'\s*[:：]','',block[pos].replace('**',''))
   if not has_content([value,*block[pos+1:stop]]):errors.append(label+'空字段：'+name)
  if positions!=sorted(positions):errors.append(label+'字段顺序不符')
 metadata=blocks.get(expected[0],[]);fields(metadata,s['metadata'],'报告信息')
 if not any(s['version'] in x and {'brief':'简版','detailed':'详细版','comprehensive':'全面版'}[depth] in x for x in metadata):errors.append('报告档位/技能版本缺失或与检查参数不符')
 fields(blocks.get(expected[1],[]),s['brief'],'简报')
 profile=s['project_brief'] if task=='project' and depth=='brief' else s['project_full'] if task=='project' else s['specialized'][task]
 appendix=s['appendix_brief'] if depth=='brief' else s['appendix_full']
 sections={}
 for top,names in [(expected[2],profile),(expected[3],appendix)]:
  top_heading=next((h for h in tops if h[2]==top),None)
  if not top_heading:continue
  start=top_heading[0];end=next((h[0] for h in tops if h[0]>start),len(lines))
  hs=[h for h in head if start<h[0]<end and h[1]==2]
  if [h[2] for h in hs]!=names:errors.append(top+'二级标题缺失、增添或顺序不符')
  for i,level,name in hs:
   body=section(i,level);sections[(top,name)]=body
   if not has_content(body):errors.append('栏目无实质文本：'+name)
   if top==expected[2] and not narrative(body):errors.append('正文栏目缺少完整说明句，不能只有表格/标签：'+name)
   if any(marker in payload(body) for marker in ['本节资料不足','本节不适用']):
    for field in s['missing_labels']:
     if not re.search(re.escape(field)+r'[:：]\s*\S',payload(body)):errors.append('缺口/不适用说明缺少'+field+'：'+name)
    waivers.append(name)
 def require_table(body,key,label,rows_expected=None):
  candidates=[rows for header,rows in tables(body) if header==s['tables'][key]]
  if not candidates:errors.append('缺少指定表头：'+label);return []
  rows=[row for group in candidates for row in group]
  if not rows:errors.append('表无数据行：'+label)
  for row in rows:
   if len(row)!=len(s['tables'][key]) or any(not x for x in row):errors.append('表列数或空值不符：'+label)
  if rows_expected is not None and sorted([r[0] for r in rows if r])!=sorted(rows_expected):errors.append('必备行缺失、重复或名称不符：'+label)
  return rows
 if task=='project' and depth!='brief':
  body=lambda name:sections.get((expected[2],name),[])
  require_table(body(s['project_full'][2]),'views','9视角',s['views'])
  require_table(body(s['project_full'][4]),'dimensions','12维',s['dimensions'])
  dp_name=s['project_full'][6]
  if dp_name not in waivers:
   dp_rows=require_table(body(dp_name),'dp','五层验证');groups=defaultdict(list)
   previous=None
   for row in dp_rows:
    if len(row)>=2:
     value=row[0]
     if value in ['同上','同前']:
      if previous is None:errors.append('五层对象承接无前项')
      else:value=previous
     else:previous=value
     groups[value].append(row[1])
   for value,layers in groups.items():
    if sorted(layers)!=sorted(s['dp']):errors.append('价值点五层不全或重复：'+value)
  q=s['project_full'][-1]
  if q not in waivers:require_table(body(q),'questions','补证问题')
 if task=='project':
  if depth=='brief':
   target=sections.get((expected[2],s['project_brief'][3]),[])
   hs=[(i,normalize(m[1])) for i,line in enumerate(target) if (m:=re.match(r'^###\s+(.+?)\s*#*$',line))]
   matches=[i for i,name in hs if name==s['esg_brief_title']]
   if len(matches)!=1:errors.append('简版缺少或重复ESG三级标题')
   else:
    start=matches[0];end=next((i for i,_ in hs if i>start),len(target));content=target[start+1:end]
    if not has_content(content) or not narrative(content):errors.append('简版ESG缺少完整说明')
    for label,pattern in [('环境',r'环境|（E）|\(E\)|(?<![A-Za-z])E\s*[:：、—-]'),('社会',r'社会|（S）|\(S\)|(?<![A-Za-z])S\s*[:：、—-]'),('治理',r'治理|（G）|\(G\)|(?<![A-Za-z])G\s*[:：、—-]')]:
     if not re.search(pattern,payload(content)):errors.append('简版ESG未标明'+label+'范围')
  else:
   target=sections.get((expected[2],s['project_full'][8]),[])
   hs=[(i,normalize(m[1])) for i,line in enumerate(target) if (m:=re.match(r'^###\s+(.+?)\s*#*$',line))]
   if [name for _,name in hs]!=s['esg_sections']:errors.append('ESG六个三级标题缺失、增添或顺序不符')
   for j,(i,name) in enumerate(hs):
    end=hs[j+1][0] if j+1<len(hs) else len(target);content=target[i+1:end]
    if not has_content(content) or not narrative(content):errors.append('ESG子节缺少完整说明：'+name)
 if depth!='brief':
  name=s['appendix_full'][0]
  if name not in waivers:require_table(sections.get((expected[3],name),[]),'evidence','关键证据')
 return {'mechanical_contract_pass':not errors,'depth':depth,'task':task,'errors':errors,'declared_waivers':waivers,'limits':'Only Markdown titles/order, field presence, table shape and limited empty/prose checks. Does not verify facts, reasoning, authorized assumptions, completed tools, fluency or investment merit; human review required.'}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('report',type=Path);p.add_argument('--depth',choices=['brief','detailed','comprehensive'],default='detailed');p.add_argument('--task',choices=['project','diligence','valuation','committee','monitoring'],default='project');a=p.parse_args()
 result=check(a.report.read_text(encoding='utf-8-sig'),a.depth,a.task);print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['mechanical_contract_pass'] else 1)
