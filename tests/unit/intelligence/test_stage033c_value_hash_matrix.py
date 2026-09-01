import importlib.util,sys,unittest,copy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[3]/"docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py"
s=importlib.util.spec_from_file_location("exv",P); m=importlib.util.module_from_spec(s); sys.modules["exv"]=m; s.loader.exec_module(m)
def inp():
 return {"schema_version":"aios-stage-0.33c-one-shot-input-v1","ingestion_result":{"input_type":"document","recognized_input_type":"pdf","stored_path":None,"manifest_path":"/opt/aios/data/documents/manifests/9801b5e4-453d-429a-b51f-e8ffaa17a2c9.json","metadata":{},"text":"","register_handoff_ready":True,"process_handoff_ready":False,"route_handoff_ready":False,"respond_acknowledgement_ready":True,"registration_succeeded":False,"registry_record_id":None,"event_publication_attempted":False,"event_delivery_succeeded":False,"event_delivery_failure_code":None,"brain_result":None},"trusted_receipt_facts":{"supplier_name":"Synthetic","document_number":None,"document_date":None,"received_at":"2025-01-01T00:00:00.000000Z","items":[{"line_number":1,"candidate_material_description":"Synthetic","canonical_display_name":None,"size_description":None,"specification":None,"material_id":None,"full_colly_count":1,"qty_per_full_colly":"2","partial_qty":"0","total_qty":"2","unit":"pcs"}]}}
class ValueHashMatrix(unittest.TestCase):
 def test_valid_ingestion_result(self): m.validate_approved_input_closed_schema(inp())
 def test_wrong_boolean(self): x=inp(); x["ingestion_result"]["route_handoff_ready"]=1; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_invalid_enum(self): x=inp(); x["ingestion_result"]["input_type"]="bad"; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_invalid_registry(self): x=inp(); x["ingestion_result"]["registration_succeeded"]=True; x["ingestion_result"]["registry_record_id"]=0; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_invalid_timestamp(self): x=inp(); x["trusted_receipt_facts"]["received_at"]="bad"; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_duplicate_lines(self): x=inp(); x["trusted_receipt_facts"]["items"].append(copy.deepcopy(x["trusted_receipt_facts"]["items"][0])); self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_bad_material(self): x=inp(); x["trusted_receipt_facts"]["items"][0]["material_id"]="notuuid"; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_bad_unit(self): x=inp(); x["trusted_receipt_facts"]["items"][0]["unit"]="lembar"; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_decimal_edges(self):
  for v in (2, "1e2", "+2", "01", "2.00", "-0", "123456789012345678901", "1.1234567"):
   x=inp(); x["trusted_receipt_facts"]["items"][0]["qty_per_full_colly"]=v; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_equation(self): x=inp(); x["trusted_receipt_facts"]["items"][0]["total_qty"]="3"; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_zero_colly(self): x=inp(); i=x["trusted_receipt_facts"]["items"][0]; i["full_colly_count"]=0; i["qty_per_full_colly"]="2"; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_positive_colly_null_qty(self): x=inp(); x["trusted_receipt_facts"]["items"][0]["qty_per_full_colly"]=None; self.assertRaises(m.GovernedStop,m.validate_approved_input_closed_schema,x)
 def test_manifest_binding(self):
  with self.assertRaises(m.GovernedStop): m.validate_manifest_evidence({"manifest_reference":"/opt/aios/data/documents/manifests/9801b5e4-453d-429a-b51f-e8ffaa17a2c9.json","manifest_id":"00000000-0000-4000-8000-000000000000"})
if __name__=="__main__": unittest.main()
