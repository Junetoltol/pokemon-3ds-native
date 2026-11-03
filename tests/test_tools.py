import importlib.util
from pathlib import Path
import tempfile
import unittest

def load(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).parents[1]/'tools'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
port=load('port');saves=load('saves')
class Tools(unittest.TestCase):
    def test_dump_header_and_rejection(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'synthetic.cxi';b=bytearray(512);b[256:260]=b'NCCH';b[280:288]=(123).to_bytes(8,'little');f.write_bytes(b)
            self.assertEqual(port.inspect_dump(f)['program_id'],'000000000000007B')
            f.write_bytes(b'invalid')
            with self.assertRaises(ValueError):port.inspect_dump(f)
    def test_backup_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'user-save';f.write_bytes(b'synthetic save test')
            a=saves.import_save(f,'y',Path(d)/'backups');b=saves.import_save(f,'y',Path(d)/'backups')
            self.assertNotEqual(a,b);self.assertEqual(a.read_bytes(),f.read_bytes());self.assertEqual(b.read_bytes(),f.read_bytes())
            with self.assertRaises(ValueError):saves.import_save(f,'../bad',d)
if __name__=='__main__':unittest.main()
