"""Optional package/privacy/prompt and calculator checks, not a model-behavior grader."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote,urlsplit
from build_prompt import build
from build_rules import render as render_rules
from build_output import build as build_output_contract

def validate(root):
    errors=[];links=0;remote=set();calc_results=[]
    paired=json.loads((root/'references/key-rules.json').read_text(encoding='utf-8'))
    if len(paired['rules'])!=14 or len({x['id'] for x in paired['rules']})!=14:errors.append('Paired rule count/IDs')
    expected='\n'+render_rules(root)+'\n'
    entry_source=(root/'SKILL.md').read_text(encoding='utf-8')
    if entry_source.split('<!-- SHARED-BEGIN -->',1)[1].split('<!-- SHARED-END -->',1)[0]!=expected:errors.append('Paired rule generation drift')
    files=sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for name in ['SKILL.md','STANDALONE_PROMPT.md','README.md','COMPATIBILITY.md','CHANGELOG.md','SOURCE_INVENTORY.md','references/finance.md','references/review.md','references/clarification.md','references/output.md','references/esg.md','references/esg-semi.md','references/esg-materials.md','references/esg-energy.md','references/esg-software.md','references/esg-health.md','references/esg-sources.md','references/output-schema.json','references/writing.md','scripts/check_output.py','tests/prompts.json','tests/rubric.json','tests/TEST_REPORT.md']:
        if not (root/name).is_file():errors.append('Missing '+name)
    entry=(root/'SKILL.md').read_text(encoding='utf-8');match=re.match(r'\A---\n(.*?)\n---\n',entry,re.S)
    if not match:errors.append('Invalid frontmatter')
    else:
        names=re.findall(r'^(\S+):',match[1],re.M);fields=dict(re.findall(r'^(name|description):\s*(.+)$',match[1],re.M));name=fields.get('name','')
        if set(names)!={'name','description'} or len(names)!=2:errors.append('Nonportable frontmatter')
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',name) or len(name)>64 or name!=root.name:errors.append('Invalid name')
        try:
            if not 1<=len(json.loads(fields.get('description','""')))<=1024:errors.append('Invalid description')
        except ValueError:errors.append('Invalid description encoding')
    confidential=[]  # Generic publication; private-source sentinel names are not distributed.
    for file in files:
        relative=file.relative_to(root).as_posix()
        if not relative.isascii():errors.append('Non-ASCII filename '+relative)
        if file.is_symlink() or getattr(file,'is_junction',lambda:False)():errors.append('Unexpected link '+relative)
        if file.suffix not in {'.md','.json','.py','.txt'}:errors.append('Unexpected file '+relative)
        data=file.read_bytes()
        try:content=data.decode('utf-8')
        except UnicodeDecodeError:errors.append('Invalid UTF-8 '+relative);continue
        if data.startswith(b'\xef\xbb\xbf') or '\ufffd' in content:errors.append('Encoding artifact '+relative)
        if file.suffix!='.py':
            patterns=[r'(?i)(?<![a-z0-9])[a-z]:[\\/]',r'/Users/[^\s/]+/',r'(?i)\bsk[-_][A-Za-z0-9_-]{16,}',r'(?i)Bearer\s+[A-Za-z0-9._-]{16,}']
            if any(re.search(x,content) for x in patterns):errors.append('Private path/credential '+relative)
            if any(''.join(map(chr,x)) in content for x in confidential):errors.append('Real-project residue '+relative)
        if file.suffix=='.json':
            try:json.loads(content)
            except ValueError:errors.append('Invalid JSON '+relative)
        if file.suffix=='.md':
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',content):
                target=target.strip('<>')
                if target.startswith(('https://','http://')):remote.add(target);continue
                if target.startswith('#'):continue
                local=(file.parent/unquote(urlsplit(target).path)).resolve()
                if not local.is_relative_to(root.resolve()) or not local.exists():errors.append('Broken link '+relative+' -> '+target)
                links+=1
    prompt=(root/'STANDALONE_PROMPT.md').read_text(encoding='utf-8')
    if prompt!=build(root):errors.append('Shared source/standalone drift')
    if re.search(r'\[[^\]]*\]\([^)]+\)',prompt):errors.append('Standalone external dependency')
    contracts={
        'SKILL.md':['默认联网核验','必须向用户提出具体问题','用户未回答不视为同意','输入—计算—用途','证据状态一致'],
        'references/clarification.md':['没有答复','不自动构成对假设的确认','已经问到答复'],
        'references/evidence.md':['搜索摘要只作线索','来源独立','逻辑互斥'],
        'references/finance.md':['算术成立不证明输入真实','亿元级披露不能自行取精确1亿元'],
        'references/review.md':['证据状态一致','未回答是否仍暂停依赖项']}
    for relative,phrases in contracts.items():
        source=(root/relative).read_text(encoding='utf-8')
        for phrase in phrases:
            if phrase not in source or phrase not in prompt:errors.append('Literal rule contract missing '+relative+' / '+phrase)
    if (root/'references/output.md').read_text(encoding='utf-8')!=build_output_contract(root):errors.append('Output schema/document drift')
    for rel,phrases in {'SKILL.md':['固定15节','输出以人阅读为目标'], 'references/output.md':['唯一的正式输出要求','十五个二级标题固定','不得静默省略'], 'references/writing.md':['输出以人阅读为目标','完整、连贯的中文','不能全文只有表格']}.items():
        content=(root/rel).read_text(encoding='utf-8')
        for phrase in phrases:
            if phrase not in content or phrase not in prompt:errors.append('Output/writing rule not synchronized: '+rel+' / '+phrase)
    proc=subprocess.run([sys.executable,'-X','utf8',str(root/'scripts/test_output.py')],capture_output=True,text=True,encoding='utf-8',timeout=30)
    try:checker=json.loads(proc.stdout)
    except (ValueError,TypeError):checker={'all_checker_tests_passed':False,'error':'No checker-test JSON'}
    if proc.returncode!=0 or not checker.get('all_checker_tests_passed'):errors.append('Mechanical checker tests failed')
    cases=json.loads((root/'tests/prompts.json').read_text(encoding='utf-8'))['cases'];rubric=json.loads((root/'tests/rubric.json').read_text(encoding='utf-8'))['criteria'];ids=[x['id'] for x in cases]
    if len(ids)!=len(set(ids)) or set(ids)!=set(rubric):errors.append('Case/rubric mismatch')
    if {x['task'] for x in cases}!={'screening','diligence','valuation','committee','monitoring'}:errors.append('Missing lifecycle coverage')
    fixtures=json.loads((root/'tests/calc_cases.json').read_text(encoding='utf-8'))
    for index,fixture in enumerate(fixtures,1):
        proc=subprocess.run([sys.executable,'-X','utf8',str(root/'scripts/calc.py')],input=json.dumps(fixture['input']),text=True,encoding='utf-8',capture_output=True,timeout=10)
        expected=fixture['expected'];passed=False
        if expected=='error':passed=proc.returncode==2
        elif proc.returncode==0:
            actual=json.loads(proc.stdout)['result'];passed=True
            for key,value in expected.items():
                got=actual.get(key)
                if isinstance(value,list):passed=passed and isinstance(got,list) and len(got)==len(value) and all(math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8) for a,b in zip(got,value))
                else:passed=passed and math.isclose(got,value,rel_tol=1e-9,abs_tol=1e-8)
        calc_results.append({'fixture':index,'passed':passed,'rejected_invalid_input':expected=='error'})
        if not passed:errors.append('Calculator fixture '+str(index))
    manifest=root/'PACKAGE_MANIFEST.json'
    if manifest.is_file():
        for item in json.loads(manifest.read_text(encoding='utf-8'))['files']:
            path=root/item['path']
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:errors.append('Manifest mismatch '+item['path'])
    return {'structural_pass':not errors,'files':len(files),'local_links_checked':links,'anonymous_cases':len(cases),'standalone_characters':len(prompt),'calculator_results':calc_results,'reference_urls':sorted(remote),'mechanical_checker_tests':checker,'rule_contract_kind':'literal presence and shared generation only; not behavior grading','errors':errors,'limits':'Structure, exact prompt generation and real calculator executions only; not model behavior, external facts or native discovery.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('skill_directory',type=Path);args=parser.parse_args();result=validate(args.skill_directory.resolve());print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['structural_pass'] else 1)
