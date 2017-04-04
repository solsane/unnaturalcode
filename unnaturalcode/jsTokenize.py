import bond
from pathlib import Path
import os
import mmap
import tempfile
from logging import error
import json
import resource
pagesize = resource.getpagesize()


class JSTokenizer(object):
    def __init__(self):
        THIS_DIRECTORY = Path(__file__).parent.parent
        TOKENIZE_JS_BIN = (str(THIS_DIRECTORY / 'tokenize-js' / 'wrapper.sh'),)
        assert os.path.exists(TOKENIZE_JS_BIN[0]), TOKENIZE_JS_BIN[0]
        CHECK_SYNTAX_BIN = (TOKENIZE_JS_BIN[0], '--check-syntax')

        js = bond.make_bond('JavaScript', 
                            cwd=str(THIS_DIRECTORY / 'tokenize-js'),
                            timeout=600,
                            )
        js.eval_block("""
        const tokenize = require('./tokenize');
        """)
        
        self.js = js
        self.tf = tempfile.NamedTemporaryFile('w+b')
        #self.tf.truncate(pagesize)
        self.tf.truncate(1024*1024*1024)
        self.mm = mmap.mmap(self.tf.fileno(), 0)
        js.call('tokenize.connect', self.tf.name, self.mm.size())
    
    def tokenize(self, src):
        self.mm.seek(0)
        srcbytes = src.encode('UTF-8')
        self.mm.write(srcbytes)
        sz = self.js.call('tokenize.tokenize', len(srcbytes))
        #if (sz > self.mm.size):
            #newsize = math.ceil(sz/pagesize)*pagesize
            #self.mm.close()
            #self.tf.truncate(newsize)
            #self.mm = mmap.mmap(self.tf.fileno(), 0)
        assert sz < self.mm.size()
        self.mm.seek(0)
        raw = self.mm.read(sz)
        assert len(raw) == sz, " ".join(map(str, (sz, self.mm.size(), len(raw))))
        raw = json.loads(raw.decode('UTF-8'))
        return raw
      
    def check_syntax(self, src):
        self.mm.seek(0)
        srcbytes = src.encode('UTF-8')
        self.mm.write(srcbytes)
        return self.js.call('tokenize.checkSyntax', len(srcbytes))
