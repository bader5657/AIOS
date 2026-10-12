from pathlib import Path
SOURCE=Path(__file__).with_name('verify_telegram_e2e.py').read_text(encoding='utf-8-sig')

import ast, asyncio
from types import SimpleNamespace
tree = ast.parse(SOURCE)
main_node = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "main")
owner_branch = next(n for n in ast.walk(main_node) if isinstance(n, ast.If) and isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Attribute) and n.test.left.attr == "id")
probe = ast.AsyncFunctionDef(name="probe",args=ast.arguments(posonlyargs=[],args=[ast.arg(arg=k) for k in ("message","bot","state","owner","expected_confirmation","update")],kwonlyargs=[],kw_defaults=[],defaults=[]),body=[owner_branch],decorator_list=[])
ns={"FIXTURE":"catat_pelanggan synthetic", "report":lambda *args: None}
exec(compile(ast.fix_missing_locations(ast.Module(body=[probe],type_ignores=[])),"probe","exec"),ns)
class Bot:
    def __init__(self): self.sent=[]
    async def send_message(self,*args): self.sent.append(args)
async def test():
    for state in ("draft","confirm","retry"):
        bot=Bot()
        message=SimpleNamespace(from_user=SimpleNamespace(id=42),text="malformed")
        await ns["probe"](message,bot,state,42,"konfirmasi_pelanggan "+"a"*64,None)
        assert len(bot.sent)==1, "verified Owner received no guidance for malformed "+state
    bot=Bot()
    await ns["probe"](SimpleNamespace(from_user=SimpleNamespace(id=99),text="malformed"),bot,"confirm",42,"private-token",None)
    assert not bot.sent, "guidance leaked to another sender"
try:
    test().send(None)
except StopIteration:
    pass
print("OWNER_GUIDANCE_TESTS=4_PASS")
