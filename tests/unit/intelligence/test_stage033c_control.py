import importlib.util,sys,unittest,tempfile,os,pwd,json
from pathlib import Path
P=Path(__file__).resolve().parents[3]/"docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py"
s=importlib.util.spec_from_file_location("ex2",P); m=importlib.util.module_from_spec(s); sys.modules["ex2"]=m; s.loader.exec_module(m)
class ControlTests(unittest.TestCase):
 def test_uuid_sha_timestamp_safe(self):
  self.assertEqual(m.validate_uuid4_canonical_lowercase("9801b5e4-453d-429a-b51f-e8ffaa17a2c9"),"9801b5e4-453d-429a-b51f-e8ffaa17a2c9")
  with self.assertRaises(m.GovernedStop): m.validate_uuid4_canonical_lowercase("9801b5e4-453d-529a-b51f-e8ffaa17a2c9")
  with self.assertRaises(m.GovernedStop): m.validate_sha256_lowercase("A"*64)
  with self.assertRaises(m.GovernedStop): m.validate_approval_safe_string("x\x00")
 def test_duplicate_and_schema(self):
  with self.assertRaises(m.GovernedStop): m.exact_json(b'{"a":1,"a":2}')
  with self.assertRaises(m.GovernedStop): m.validate_approval_closed_schema({"schema_version":"x"})
 def test_failure_result_minimized(self):
  with tempfile.TemporaryDirectory() as d:
   fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY); st=m.ExecutionState(executor_sha="a"*64); f=m.GovernedStop(m.APPROVED_BYTES_INVALID,"TEST","input",22); m.write_failure_result(fd,st,f); data=Path(d,m.RESULT).read_text(); self.assertNotIn("traceback",data); self.assertNotIn("supplier",data); os.close(fd)
if __name__=="__main__": unittest.main()
