"""Render paired rules into the entry. Does not assess translation quality."""
from pathlib import Path
import argparse,json,re

def render(root):
 data=json.loads((root/'references/key-rules.json').read_text(encoding='utf-8'))
 rules=data['rules'];assert len(rules)==14 and len({r['id'] for r in rules})==14
 for r in rules:assert r['zh'].strip() and r['en'].strip()
 blocks=['## 共同执行规则 / Key rules',
 '以下中英文表达同一组约束，不增加第二套工作流，也不指定内部推理语言。英文为简明同义提示；中文限定、示例及适用制度原文仍须保留。发现影响判断的翻译歧义时核对并询问，不能自行选取更宽松版本。',
 'The paired statements express one rule set. They do not prescribe an internal reasoning language. Preserve the Chinese qualifications, examples, and applicable source texts. Resolve material translation ambiguity instead of choosing a weaker interpretation.']
 blocks += ['- '+r['zh']+'\n\n  **EN · '+r['id']+'** '+r['en'] for r in rules]
 blocks += [data['closing_zh']]
 return '\n\n'.join(blocks)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();root=Path(__file__).resolve().parents[1];f=root/'SKILL.md';text=f.read_text(encoding='utf-8');body=render(root)
 expected=re.sub(r'(?s)(<!-- SHARED-BEGIN -->).*?(<!-- SHARED-END -->)',lambda m:m[1]+'\n'+body+'\n'+m[2],text,count=1)
 if a.check:assert text==expected,'Paired rule source drift'
 else:f.write_text(expected,encoding='utf-8',newline='\n')
 print(('Checked' if a.check else 'Built')+' 14 paired key rules')
