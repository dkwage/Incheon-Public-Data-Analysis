"""Collect public data snapshots. Key: DATA_GO_KR_SERVICE_KEY or existing sample notebook."""
import ast
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw"

def service_key():
    key = os.environ.get("DATA_GO_KR_SERVICE_KEY")
    if key:
        return key
    # Reuse the user's existing credential without copying it into another file.
    notebook = json.loads((ROOT / "sample.ipynb").read_text())
    for cell in notebook["cells"]:
        source = "".join(cell.get("source", []))
        if cell["cell_type"] != "code" or "SERVICE_KEY =" not in source:
            continue
        for node in ast.parse(source).body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SERVICE_KEY" for t in node.targets):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    return node.value.value
    raise RuntimeError("DATA_GO_KR_SERVICE_KEY 환경변수를 설정하세요.")

def fetch(name, url, params, kind="odcloud", max_pages=300):
    path = RAW / (name + ".json")
    if path.exists():
        saved = json.loads(path.read_text())
        if saved.get("complete") and saved.get("params") == params and saved.get("url") == url:
            print(name, "cached", len(saved["rows"]), flush=True)
            return saved
    rows, expected, stdr = [], None, None
    api_key = service_key()
    for page in range(1, max_pages + 1):
        paging = {"pageNo": page, "numOfRows": 1000, "type": "json"} if kind == "store" else {"page": page, "perPage": 1000}
        query = {**params, **paging, "serviceKey": api_key}
        try:
            with urlopen(url + "?" + urlencode(query), timeout=45) as response:
                data = json.load(response)
        except Exception as exc:
            raise RuntimeError(f"{name} page {page}: {type(exc).__name__} (인증키 보호를 위해 URL 생략)") from None
        if kind == "store":
            header = data.get("header", {})
            if header.get("resultCode") != "00":
                raise RuntimeError(f"{name}: API resultCode={header.get('resultCode')}")
            body = data["body"]
            batch = body["items"]
            total = int(body["totalCount"])
            current_stdr = header.get("stdrYm")
            if page > 1 and current_stdr != stdr:
                raise RuntimeError("수집 중 점포 기준월 변경")
            stdr = current_stdr
        else:
            batch = data["data"]
            total = int(data.get("matchCount", data["totalCount"]))
        if expected is not None and total != expected:
            raise RuntimeError(f"{name}: 수집 중 전체 건수 변경")
        expected = total
        if not isinstance(batch, list):
            raise ValueError("API rows must be a list")
        rows.extend(batch)
        if len(rows) >= expected:
            if len(rows) != expected:
                raise RuntimeError(f"{name}: 전체 건수 초과")
            break
        if not batch:
            raise RuntimeError(f"{name}: 전체 건수 도달 전 빈 페이지")
    else:
        raise RuntimeError(f"{name}: 페이지 한도 도달, 부분 자료 저장 안 함")
    result = dict(url=url, params=params, retrieved_at=datetime.now(timezone.utc).isoformat(),
                  standard_month=stdr, total=expected, complete=True, rows=rows)
    RAW.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)
    print(name, len(rows), "complete", flush=True)
    return result

if __name__ == "__main__":
    fetch("district_stores", "https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInDong",
          {"divId": "signguCd", "key": "28177"}, "store")
    base = "https://api.odcloud.kr/api/"
    fetch("market", base + "15087058/v1/uddi:d5a7f08b-59b0-4692-a211-86ae19d64477", {})
    fetch("bus_stop", base + "15048264/v1/uddi:931f0ff0-d7b6-4fa2-8088-e4c973a6b56e", {})
    fetch("bus_location_incheon", base + "15067528/v1/uddi:f74b9799-9db1-4754-a5d0-b66e2ae705f3",
          {"cond[도시명::LIKE]": "인천"})
