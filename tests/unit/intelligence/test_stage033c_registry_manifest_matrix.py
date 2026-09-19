import copy,hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
REPOSITORY_ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPOSITORY_ROOT))
P=Path(__file__).resolve().parents[3]/"docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py"
s=importlib.util.spec_from_file_location("ex_matrix",P); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)
MID="9801b5e4-453d-429a-b51f-e8ffaa17a2c9"; REF=f"/opt/aios/data/documents/manifests/{MID}.json"; WHEN="2026-08-18T10:11:12.123456Z"
def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def input_obj(success=False,rid=None):
 return {"schema_version":"aios-stage-0.33c-one-shot-input-v1","ingestion_result":{"input_type":"document","recognized_input_type":"pdf","stored_path":None,"manifest_path":REF,"metadata":{},"text":"","register_handoff_ready":True,"process_handoff_ready":False,"route_handoff_ready":False,"respond_acknowledgement_ready":True,"registration_succeeded":success,"registry_record_id":rid,"event_publication_attempted":False,"event_delivery_succeeded":False,"event_delivery_failure_code":None,"brain_result":None},"trusted_receipt_facts":{"supplier_name":"Synthetic Supplier","document_number":None,"document_date":None,"received_at":WHEN,"items":[{"line_number":1,"candidate_material_description":"Synthetic Item","canonical_display_name":None,"size_description":None,"specification":None,"material_id":None,"full_colly_count":1,"qty_per_full_colly":"2","partial_qty":"0","total_qty":"2","unit":"pcs"}]}}
def rehash(f):
 a=f["approval"]; a["package_payload_sha256"]=hashlib.sha256(canon(a["package_payload"])).hexdigest(); return canon(a)+b"\n"
def tf_a_or_existing(f):
 try: return m.trusted_facts_dto_sha256(f["input"]["trusted_receipt_facts"])
 except m.GovernedStop: return f["approval"]["package_payload"]["trusted_facts_sha256"]
def refresh(f):
 f["input_transport"]=canon(f["input"])+b"\n"; p=f["approval"]["package_payload"]; p["input_semantic_sha256"]=hashlib.sha256(f["input_transport"][:-1]).hexdigest(); p["input_transport_sha256"]=hashlib.sha256(f["input_transport"]).hexdigest(); p["input_semantic_bytes"]=len(f["input_transport"])-1; p["input_transport_bytes"]=len(f["input_transport"]); p["trusted_facts_sha256"]=tf_a_or_existing(f); return rehash(f)
def fixture(root,success=False,rid=None):
 root=Path(root); retained=root/"retained"; od=retained/"pdf"; mr=root/"manifests"; od.mkdir(parents=True); mr.mkdir(); original=od/"synthetic.bin"; ob=b"synthetic retained bytes only"; original.write_bytes(ob); osh=hashlib.sha256(ob).hexdigest(); manifest={"manifest_id":MID,"represented_media_type":"pdf","received_at":WHEN,"manifest_status":"created","metadata":{"media_type":"pdf","file_size_bytes":len(ob),"mime_type":"application/pdf"},"storage_path":str(original),"file_size_bytes":len(ob),"checksum_sha256":osh}; mb=canon(manifest); mp=mr/f"{MID}.json"; mp.write_bytes(mb); inp=input_obj(success,rid); it=canon(inp)+b"\n"; ev={"manifest_reference":REF,"manifest_id":MID,"manifest_sha256":hashlib.sha256(mb).hexdigest(),"manifest_size_bytes":len(mb),"represented_media_type":"pdf","manifest_received_at":WHEN,"stored_original_size_bytes":len(ob),"stored_original_sha256":osh,"mime_type":"application/pdf","registry_record_id":rid}; p={"approval_id":"12345678-1234-4abc-8def-1234567890ab","approved_at_utc":"2098-01-01T00:00:00.000000Z","not_after_utc":"2099-01-01T00:00:00.000000Z","project_owner_approval_reference":"SYNTHETIC-APPROVAL","repository_commit":"a"*40,"harness_sha256":m.HARNESS_SHA256,"python_path":"/opt/aios/runtime/venv/bin/python","python_version":"3.12.3","controlled_callable":"core.app.material_receipts.controlled_candidate_create.controlled_create_review_candidate","evidence":ev,"trusted_facts_sha256":m.trusted_facts_dto_sha256(inp["trusted_receipt_facts"]),"input_semantic_sha256":hashlib.sha256(it[:-1]).hexdigest(),"input_transport_sha256":hashlib.sha256(it).hexdigest(),"input_semantic_bytes":len(it)-1,"input_transport_bytes":len(it),"item_count":1,"trusted_fact_provenance":{k:"EVIDENCE_DERIVED" for k in m.expected_provenance_pointers(1)},"more_than_three_items_justification":None}; a={"schema_version":"aios-stage-0.33c-step4-approved-input-v1","package_payload":p}; f={"root":root,"retained":retained,"manifest_root":mr,"original":original,"manifest_path":mp,"manifest":manifest,"input":inp,"input_transport":it,"approval":a}; rehash(f); return f
def validate(f,at=None): return m.validate_frozen_package(f["input_transport"],at or rehash(f),manifest_root=f["manifest_root"],retained_root=f["retained"])
def invalid(tc,f,at=None):
 with tc.assertRaises(m.GovernedStop) as c: validate(f,at)
 tc.assertEqual(c.exception.classification,m.APPROVED_BYTES_INVALID)
class Base(unittest.TestCase):
 def f(self,**kw): t=tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup); return fixture(t.name,**kw)
class RegistryModelBMatrix(Base):
 def test_registry_01_valid_null(self): validate(self.f())
 def test_registry_02_valid_positive(self): validate(self.f(success=True,rid=42))
 def test_registry_03_mismatch(self): f=self.f(success=True,rid=42); f["approval"]["package_payload"]["evidence"]["registry_record_id"]=43; invalid(self,f)
 def test_registry_04_false_nonnull(self): f=self.f(); f["input"]["ingestion_result"]["registry_record_id"]=7; refresh(f); invalid(self,f)
 def test_registry_05_true_null(self): f=self.f(); f["input"]["ingestion_result"]["registration_succeeded"]=True; refresh(f); invalid(self,f)
 def bad(self,v): f=self.f(); f["input"]["ingestion_result"].update(registration_succeeded=True,registry_record_id=v); f["approval"]["package_payload"]["evidence"]["registry_record_id"]=v; refresh(f); invalid(self,f)
 def test_registry_06_zero(self): self.bad(0)
 def test_registry_07_negative(self): self.bad(-1)
 def test_registry_08_oversized(self): self.bad(9223372036854775808)
 def test_registry_09_wrong_types(self):
  for v in (True,"42",42.0,[]):
   with self.subTest(v=v): self.bad(v)
 def test_registry_10_handoff_independent(self): f=self.f(); self.assertTrue(f["input"]["ingestion_result"]["register_handoff_ready"]); self.assertFalse(f["input"]["ingestion_result"]["registration_succeeded"]); validate(f)
 def test_registry_11_hash_tamper(self): f=self.f(); rehash(f); f["approval"]["package_payload"]["evidence"]["registry_record_id"]=9; invalid(self,f,canon(f["approval"])+b"\n")
 def test_registry_13_false_boolean_id(self): self.bad(False)
 def test_registry_12_no_postgresql(self): src=P.read_text().lower(); self.assertNotIn("psycopg",src); self.assertNotIn("asyncpg",src); self.assertNotIn("create_connection(",src)
class CoreValueHash25(Base):
 def reject(self,fn): f=self.f(); fn(f["input"]); refresh(f); invalid(self,f)
 def test_core_01_valid(self): validate(self.f())
 def test_core_20_trusted_sha(self): f=self.f(); f["approval"]["package_payload"]["trusted_facts_sha256"]="0"*64; invalid(self,f)
 def test_core_21_semantic_sha(self): f=self.f(); f["approval"]["package_payload"]["input_semantic_sha256"]="0"*64; invalid(self,f)
 def test_core_22_transport_sha(self): f=self.f(); f["approval"]["package_payload"]["input_transport_sha256"]="0"*64; invalid(self,f)
 def test_core_23_payload_sha(self): f=self.f(); rehash(f); f["approval"]["package_payload"]["item_count"]=2; invalid(self,f,canon(f["approval"])+b"\n")
 def test_core_24_item_count(self): f=self.f(); p=f["approval"]["package_payload"]; p["item_count"]=2; p["trusted_fact_provenance"]={k:"EVIDENCE_DERIVED" for k in m.expected_provenance_pointers(2)}; invalid(self,f)
 def test_core_26_boolean_item_count(self):
  f=self.f(); f["approval"]["package_payload"]["item_count"]=True; invalid(self,f)
 def test_core_27_boolean_input_byte_count(self):
  f=self.f(); f["approval"]["package_payload"]["input_semantic_bytes"]=True; invalid(self,f)
 def test_core_28_boolean_original_size(self):
  f=self.f(); f["approval"]["package_payload"]["evidence"]["stored_original_size_bytes"]=True; invalid(self,f)
 def test_core_25_justification(self): f=self.f(); base=f["input"]["trusted_receipt_facts"]["items"][0]; f["input"]["trusted_receipt_facts"]["items"]=[{**copy.deepcopy(base),"line_number":n} for n in range(1,5)]; refresh(f); p=f["approval"]["package_payload"]; p["item_count"]=4; p["trusted_fact_provenance"]={k:"EVIDENCE_DERIVED" for k in m.expected_provenance_pointers(4)}; invalid(self,f)
def core(name,fn):
 def test(self): self.reject(fn)
 test.__name__=name; setattr(CoreValueHash25,name,test)
core("test_core_02_wrong_boolean",lambda x:x["ingestion_result"].__setitem__("route_handoff_ready",1)); core("test_core_03_invalid_enum",lambda x:x["ingestion_result"].__setitem__("input_type","bad")); core("test_core_04_invalid_registry",lambda x:x["ingestion_result"].update(registration_succeeded=True,registry_record_id=0)); core("test_core_05_invalid_timestamp",lambda x:x["trusted_receipt_facts"].__setitem__("received_at","bad")); core("test_core_06_duplicate_line",lambda x:x["trusted_receipt_facts"]["items"].append(copy.deepcopy(x["trusted_receipt_facts"]["items"][0]))); core("test_core_07_invalid_material",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("material_id","bad")); core("test_core_08_invalid_unit",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("unit","bad")); core("test_core_09_decimal_number",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("qty_per_full_colly",2)); core("test_core_10_exponent",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("qty_per_full_colly","2e0")); core("test_core_11_plus",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("qty_per_full_colly","+2")); core("test_core_12_leading_zero",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("qty_per_full_colly","02")); core("test_core_13_trailing_zero",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("qty_per_full_colly","2.0")); core("test_core_14_negative_zero",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("partial_qty","-0")); core("test_core_15_precision",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("qty_per_full_colly","123456789012345678901")); core("test_core_16_scale",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("partial_qty","0.1234567")); core("test_core_17_equation",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("total_qty","3")); core("test_core_18_zero_colly",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("full_colly_count",0)); core("test_core_19_null_per_colly",lambda x:x["trusted_receipt_facts"]["items"][0].__setitem__("qty_per_full_colly",None))
class ManifestMatrix(Base):
 def eb(self,k,v): f=self.f(); f["approval"]["package_payload"]["evidence"][k]=v; invalid(self,f)
 def rewrite(self,f): d=canon(f["manifest"]); f["manifest_path"].write_bytes(d); e=f["approval"]["package_payload"]["evidence"]; e["manifest_sha256"]=hashlib.sha256(d).hexdigest(); e["manifest_size_bytes"]=len(d)
 def test_manifest_17_boolean_size(self): self.eb("manifest_size_bytes",True)
 def test_manifest_01_valid(self): validate(self.f())
 def test_manifest_02_reference_id(self): self.eb("manifest_id","12345678-1234-4abc-8def-1234567890ab")
 def test_manifest_03_sha(self): self.eb("manifest_sha256","0"*64)
 def test_manifest_04_size(self): f=self.f(); f["approval"]["package_payload"]["evidence"]["manifest_size_bytes"]+=1; invalid(self,f)
 def test_manifest_05_media(self): self.eb("represented_media_type","doc")
 def test_manifest_06_received(self): self.eb("manifest_received_at","2026-08-18T10:11:13.123456Z")
 def test_manifest_07_mime(self): self.eb("mime_type","application/octet-stream")
 def test_manifest_08_registry(self): self.eb("registry_record_id",1)
 def test_manifest_09_original_size(self): f=self.f(); f["approval"]["package_payload"]["evidence"]["stored_original_size_bytes"]+=1; invalid(self,f)
 def test_manifest_10_original_sha(self): self.eb("stored_original_sha256","0"*64)
 def test_manifest_11_symlink_manifest(self): f=self.f(); t=f["root"]/"target"; t.write_bytes(f["manifest_path"].read_bytes()); f["manifest_path"].unlink(); f["manifest_path"].symlink_to(t); invalid(self,f)
 def test_manifest_12_symlink_original(self): f=self.f(); t=f["retained"]/"target"; t.write_bytes(f["original"].read_bytes()); f["original"].unlink(); f["original"].symlink_to(t); invalid(self,f)
 def test_manifest_13_cross_identity(self): f=self.f(); f["input"]["ingestion_result"]["manifest_path"]="/opt/aios/data/documents/manifests/12345678-1234-4abc-8def-1234567890ab.json"; refresh(f); invalid(self,f)
 def test_manifest_14_current_schema(self): validate(self.f())
 def test_manifest_15_malformed(self): f=self.f(); del f["manifest"]["manifest_status"]; self.rewrite(f); invalid(self,f)
 def test_manifest_16_legacy(self): f=self.f(); f["manifest"]["registry_record_id"]=None; self.rewrite(f); invalid(self,f)
class FullChain(Base):
 def test_full_synthetic_chain_before_claim(self):
  f=self.f(success=True,rid=77); old=m.durable_claim
  try: m.durable_claim=lambda *a,**k:self.fail("claim reached"); i,a,manifest=validate(f)
  finally: m.durable_claim=old
  self.assertEqual(i["ingestion_result"]["registry_record_id"],77); self.assertEqual(a["package_payload"]["evidence"]["registry_record_id"],77); self.assertEqual(manifest["manifest_id"],MID)
if __name__=="__main__": unittest.main()
