import hashlib
import json
import os
import subprocess


class PwshRequests:
    __module__ = "src"

    @staticmethod
    def _calculate_hash(data_json):
        sha256 = hashlib.sha256()
        sha256.update(data_json.encode("utf-8"))
        return sha256.hexdigest()

    @staticmethod
    def _run_ps1_script(data_json, cache_dir):
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
        result = subprocess.run(command, capture_output=True, text=True)
        return result

    @staticmethod
    def _load_from_cache(hash_name, cache_dir):
        cache_file = os.path.join(cache_dir, f"{hash_name}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                return f.read()
        return None

    @staticmethod
    def request(
        method, url, headers=None, data=None, cache=False, cache_dir=".\\.cache"
    ):
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

        if result.returncode != 0:
            raise Exception(f"Request failed: {result.stderr}")

        response_content = result.stdout

        if cache:
            cache_file = os.path.join(cache_dir, f"{hash_name}.json")
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(response_content)

        return response_content

    @staticmethod
    def get(url, headers=None, cache=False, cache_dir=".\\.cache"):
        return PwshRequests.request(
            "GET", url, headers=headers, cache=cache, cache_dir=cache_dir
        )

    @staticmethod
    def post(url, headers=None, data=None, cache=False, cache_dir=".\\.cache"):
        return PwshRequests.request(
            "POST", url, headers=headers, data=data, cache=cache, cache_dir=cache_dir
        )

    @staticmethod
    def put(url, headers=None, data=None):
        return PwshRequests.request("PUT", url, headers=headers, data=data)

    @staticmethod
    def delete(url, headers=None):
        return PwshRequests.request("DELETE", url, headers=headers)
