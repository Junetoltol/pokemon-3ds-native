import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).parents[1]/'tools'))

def load(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).parents[1]/'tools'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
port=load('port');saves=load('saves')
import run_local
class Tools(unittest.TestCase):
    def test_runtime_zero_exit_does_not_prove_boot(self):
        self.assertFalse(run_local.headless_passed('could not load game', 120, 0))
        self.assertFalse(run_local.headless_passed('Completed after 1 frames', 120, 0))
        self.assertFalse(run_local.headless_passed('Completed after 120 frames\nfatal errors: failed',120,0))
        self.assertFalse(run_local.headless_passed('Completed after 120 frames',120,1))
        self.assertTrue(run_local.headless_passed('Completed after 120 frames in 2s',120,0))
    def test_game_identity_cannot_be_relabelled(self):
        info={'program_id': '00040000001B5000', 'encrypted': False}
        port.validate_profile(info, 'ultra-sun')
        with self.assertRaises(ValueError):port.validate_profile(info, 'y')
        with self.assertRaises(ValueError):port.validate_profile(info | {'encrypted': True}, 'ultra-sun')
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
