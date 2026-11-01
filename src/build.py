import json,sys
t=open('template.html').read()
ledger=json.load(open('ledger.json')); key=json.load(open('answer_key.json'))
run = open(sys.argv[1]).read().strip() if len(sys.argv)>1 else 'null'
s=lambda o: json.dumps(o,separators=(',',':')).replace('</','<\\/')
t=t.replace('/*__LEDGER__*/',s(ledger)).replace('/*__KEY__*/',s(key)).replace('/*__RUN__*/',run.replace('</','<\\/'))
standalone = len(sys.argv)>2 and sys.argv[2]=='standalone'
t=t.replace('/*__STANDALONE__*/false','true' if standalone else 'false')
out = sys.argv[3] if len(sys.argv)>3 else 'index.html'
open(out,'w').write(t); print(out,len(t))
