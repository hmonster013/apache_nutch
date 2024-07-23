import requests
import json
import subprocess
import time

def wait_for_job_completion(job_id, url):
    while True:
        response = requests.get(f"{url}/job/{job_id}")
        status = response.json()

        if status.get('state') == 'FINISHED':
            return status
        elif status.get('state') == 'FAILED':
            return status

        time.sleep(5) 

def inject(URL):
    """# bin/nutch inject crawl/crawldb urls
    """
    data = {
        "type":"INJECT",
        "confId":"default",
        "crawlId":"crawl",
        "args": {"url_dir":"urls/"}
    }


    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=URL + "/job/create",
                             data=json.dumps(data),
                             headers=headers,
                             timeout=15)
    data = response.json()

    return wait_for_job_completion(data.get("id"), URL)

def generate(URL, topN):
    """bin/nutch generate crawl/crawldb crawl/segments
    """
    data = {  
        "type":"GENERATE",
        "confId":"default",
        "crawlId":"crawl",
        "args": {
            "topN": topN
        }
    }


    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=URL + "/job/create",
                             data=json.dumps(data),
                             headers=headers,
                             timeout=15)

    data = response.json()

    return wait_for_job_completion(data.get("id"), URL)

def get_path_name(container_name="apache_nutch"):
    """s1=`ls -d crawl/segments/2* | tail -1`
			echo $s1
    """
    command = "ls -d nutch/crawl/segments/2* | tail -1"
    # Tạo lệnh docker exec
    full_command = ['docker', 'exec', container_name, 'sh', '-c', command]

    # Chạy lệnh và thu thập đầu ra
    result = subprocess.run(full_command, capture_output=True, text=True, check=False)

    # Kiểm tra mã thoát và in đầu ra
    if result.returncode == 0:
        return result.stdout
    else:
        print("Error:\n", result.stderr)

    return ""


def fetch(URL, segments):
    """bin/nutch fetch $s1
    """
    data = {  
        "type":"FETCH",
        "confId":"default",
        "crawlId":"crawl",
        "args": {
            "segments": segments
        }
    }


    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=URL + "/job/create",
                             data=json.dumps(data),
                             headers=headers,
                             timeout=15)

    data = response.json()

    return wait_for_job_completion(data.get("id"), URL)

def parse(URL, segments):
    """bin/nutch parse $s1
    """
    data = {  
        "type":"PARSE",
        "confId":"default",
        "crawlId":"crawl",
        "args": {
            "segments": segments
        }
    }


    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=URL + "/job/create",
                             data=json.dumps(data),
                             headers=headers,
                             timeout=15)

    data = response.json()

    return wait_for_job_completion(data.get("id"), URL)

def updatedb(URL, segments):
    """bin/nutch updatedb crawl/crawldb $s1
    """
    data = {  
        "type":"UPDATEDB",
        "confId":"default",
        "crawlId":"crawl",
        "args": {
            "segments": segments
        }
    }


    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=URL + "/job/create",
                             data=json.dumps(data),
                             headers=headers,
                             timeout=15)

    data = response.json()

    return wait_for_job_completion(data.get("id"), URL)

def process(URL, data):
    """bin/nutch generate crawl/crawldb crawl/segments -topN 5000
			s2=`ls -d crawl/segments/2* | tail -1`
			echo $s2

			bin/nutch fetch $s2
			bin/nutch parse $s2
			bin/nutch updatedb crawl/crawldb $s2
        + Chúng ta hãy thu thập thêm một vòng nữa:

			bin/nutch generate crawl/crawldb crawl/segments -topN 10000
			s3=`ls -d crawl/segments/2* | tail -1`
			echo $s3

			bin/nutch fetch $s3
			bin/nutch parse $s3
			bin/nutch updatedb crawl/crawldb $s3
    """
    print("Generate result:" + str(generate(URL=URL, topN=data['topN'])))
    print("Fetch result:" + str(fetch(URL=URL, segments=get_path_name())))
    print("Parse result:" + str(parse(URL=URL, segments=get_path_name())))
    print("UpdateDB result:" + str(updatedb(URL=URL, segments=get_path_name())))

def invertlinks(URL):
    """bin/nutch invertlinks crawl/linkdb -dir crawl/segments
    """
    data = {
        "type":"INVERTLINKS",
        "confId":"default",
        "crawlId":"crawl",
        "args": {}
    }


    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=URL + "/job/create",
                             data=json.dumps(data),
                             headers=headers,
                             timeout=15)

    data = response.json()

    return wait_for_job_completion(data.get("id"), URL)

def index(URL, segments, linkdb, filter, normalize, deleteGone):
    """bin/nutch index crawl/crawldb/ -linkdb crawl/linkdb/ crawl/segments/20131108063838/ -filter -normalize -deleteGone
    """
    data = {
        "type":"INDEX",
        "confId":"default",
        "crawlId":"crawl",
        "args": {
            "-linkdb": linkdb,
            "segments": segments,
            "-filter": filter,
            "-normalize": normalize,
            "-deleteGone": deleteGone
        }
    }


    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=URL + "/job/create",
                             data=json.dumps(data),
                             headers=headers,
                             timeout=15)

    data = response.json()

    return wait_for_job_completion(data.get("id"), URL)

if __name__ == "__main__":
    URL_CORE = "http://localhost:8081"
    data = {
        "topN": "50000",
        "-linkdb": "crawl/linkdb/",
        "filter": True,
        "normalize": True,
        "deleteGone": True
    }
    # print(inject(URL=URL_CORE))
    # print(generate(URL=URL_CORE, topN=data["topN"]))
    # print(fetch(URL=URL_CORE, segments=get_path_name()))
    # print(parse(URL=URL_CORE, segments=get_path_name()))
    # print(updatedb(URL=URL_CORE, segments=get_path_name()))

    process(URL=URL_CORE, data=data)

    print(index(URL=URL_CORE,
          segments=get_path_name(),
          linkdb=data["-linkdb"],
          filter=data["filter"],
          normalize=data["normalize"],
          deleteGone=data["deleteGone"]))
