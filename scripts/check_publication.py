"""Check publication integrity, local links, and common private path/secret shapes. No model calls."""
from pathlib import Path
import hashlib,json,re
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[1]
def main():
 errors=[];files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.git','__pycache__'])]
 for p in files:
  rel=p.relative_to(ROOT).as_posix()
  if p.suffix not in {'.md','.py','.json'} and p.name!='.gitignore':errors.append('Unapproved file type: '+rel);continue
  try:t=p.read_text(encoding='utf-8')
  except UnicodeDecodeError:errors.append('Not UTF-8: '+rel);continue
  patterns=[r'(?i)(?<![a-z0-9])[a-z]:[\\/]',r'(?i)\bsk[-_][A-Za-z0-9_-]{20,}',r'(?i)Bearer\s+[A-Za-z0-9._-]{20,}']
  if any(re.search(q,t) for q in patterns):errors.append('Private-path/credential shape: '+rel)
  if p.suffix=='.md':
   for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',t):
    link=link.strip('<>')
    if link.startswith(('https://','http://','#')):continue
    target=(p.parent/unquote(urlsplit(link).path)).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.exists():errors.append('Broken local link: '+rel+' -> '+link)
 checks=ROOT/'CHECKSUMS.json'
 if checks.is_file():
  for item in json.loads(checks.read_text(encoding='utf-8'))['files']:
   p=ROOT/item['path']
   if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:errors.append('Checksum mismatch: '+item['path'])
 result={'publication_checks_passed':not errors,'files_checked':len(files),'errors':errors,'scope':'Local structure, selected text patterns and file integrity; not rights, model behavior or investment facts.'}
 print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if not errors else 1
if __name__=='__main__':raise SystemExit(main())
