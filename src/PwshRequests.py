import hashlib
import json
import os
import subprocess
from typing import Optional

class PwshRequests:
    __module__ = "nekobendUtils"

    @staticmethod
    def _calculate_hash(data_json: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(data_json.encode("utf-8"))
        return sha256.hexdigest()

    @staticmethod
    def _run_ps1_script(data_json: str, cache_dir: str) -> subprocess.CompletedProcess:
        command = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "REQUESTS.PS1",
            "-dataJson",
            data_json,
            "-dir",
            cache_dir,
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result
        except subprocess.CalledProcessError as e:
            raise Exception(f"Request failed: {e.stderr}")

    @staticmethod
    def _load_from_cache(hash_name: str, cache_dir: str) -> Optional[str]:
        cache_file = os.path.join(cache_dir, f"{hash_name}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                return f.read()
        return None

    @staticmethod
    def request(
        method: str, url: str, headers: Optional[dict] = None, data: Optional[dict] = None, cache: bool = False, cache_dir: str = "./.cache"
    ) -> str:
        if method.upper() in ["PUT", "DELETE"]:
            cache = False
        if cache and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        request_dict = {
            "URL": url,
            "Method": method.upper(),
            "Headers": headers or {},
            "Body": data or {},
        }
        data_json = json.dumps(request_dict)
        hash_name = PwshRequests._calculate_hash(data_json)

        if cache:
            cached_response = PwshRequests._load_from_cache(hash_name, cache_dir)
            if cached_response is not None:
                return cached_response

        result = PwshRequests._run_ps1_script(data_json, cache_dir)

        response_content = result.stdout

        if cache:
            cache_file = os.path.join(cache_dir, f"{hash_name}.json")
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(response_content)

        return response_content

    @staticmethod
    def get(url: str, headers: Optional[dict] = None, cache: bool = False, cache_dir: str = "./.cache") -> str:
        return PwshRequests.request(
            "GET", url, headers=headers, cache=cache, cache_dir=cache_dir
        )

    @staticmethod
    def post(url: str, headers: Optional[dict] = None, data: Optional[dict] = None, cache: bool = False, cache_dir: str = "./.cache") -> str:
        return PwshRequests.request(
            "POST", url, headers=headers, data=data, cache=cache, cache_dir=cache_dir
        )

    @staticmethod
    def put(url: str, headers: Optional[dict] = None, data: Optional[dict] = None) -> str:
        return PwshRequests.request("PUT", url, headers=headers, data=data)

    @staticmethod
    def delete(url: str, headers: Optional[dict] = None) -> str:
        return PwshRequests.request("DELETE", url, headers=headers)