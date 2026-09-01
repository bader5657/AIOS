import importlib.util, tempfile, unittest, os, re, sys
from pathlib import Path
P=Path(__file__).resolve().parents[3]/"docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py"
s=importlib.util.spec_from_file_location("ex",P); ex=importlib.util.module_from_spec(s); sys.modules["ex"]=ex; s.loader.exec_module(ex)
class FilesystemTests(unittest.TestCase):
 def test_stage_names(self):
  for n in ("approved-input.json","approved-input-approval.json"):
   x=ex.make_stage_name(n); self.assertRegex(x, rf"^\.{re.escape(n)}\.stage-[0-9a-f]{{8}}-[0-9a-f]{{4}}-4[0-9a-f]{{3}}-[89ab][0-9a-f]{{3}}-[0-9a-f]{{12}}$")
 def test_link_inode_and_cleanup(self):
  with tempfile.TemporaryDirectory() as d:
   fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY); stage=ex.make_stage_name("approved-input.json"); final="approved-input.json"
   w=os.open(stage,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600,dir_fd=fd); os.write(w,b"x\n"); os.fsync(w); os.close(w); os.chmod(os.path.join(d,stage),0o440)
   os.link(stage,final,src_dir_fd=fd,dst_dir_fd=fd); a=os.stat(os.path.join(d,stage)); b=os.stat(os.path.join(d,final)); self.assertEqual(a.st_ino,b.st_ino); os.unlink(stage,dir_fd=fd); self.assertFalse(os.path.lexists(os.path.join(d,stage))); os.close(fd)
 def test_verify_returns_metadata(self):
  with tempfile.TemporaryDirectory() as d:
   fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY); n="approved-input.json"; path=os.path.join(d,n); Path(path).write_bytes(b"{}\n"); os.chmod(path,0o440); os.chown(path,0,os.getgid()) if os.geteuid()==0 else None
   if os.geteuid()!=0: self.skipTest("root metadata")
   m=ex.verify_file(fd,n,b"{}\n",2,ex.sha256(b"{}")); self.assertGreater(m.st_ino,0); os.close(fd)
if __name__=="__main__": unittest.main()
