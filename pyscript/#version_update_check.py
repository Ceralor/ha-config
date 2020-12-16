# %%
import requests
from jsonpath_ng.ext import parse
ha_core_github_url = "https://api.github.com/repos/home-assistant/home-assistant/releases/latest"
ha_core_docker_url = "https://hub.docker.com/v2/repositories/homeassistant/home-assistant/tags"
r = requests.get(ha_core_github_url)
ha_core_release_tag = r.json()['tag_name']
ha_core_release_tag = "dev"
r = requests.get(ha_core_docker_url)
docker_json = r.json()
stable_shahash_path = "$.results[?(@.name=='stable')].images[?(@.architecture=='amd64')].digest"
version_shahash_path = "$.results[?(@.name=='"+ha_core_release_tag+"')].images[?(@.architecture=='amd64')].digest"
docker_tag_parser = parse("$.results[*].name")
docker_tags = [x.value for x in docker_tag_parser.find(docker_json)]
if ha_core_release_tag in docker_tags:
    stable_shahash_parser = parse(stable_shahash_path)
    version_shahash_parser = parse(version_shahash_path)
    stable_shahash = stable_shahash_parser.find(docker_json)[0].value
    version_shahash = version_shahash_parser.find(docker_json)[0].value
    if stable_shahash == version_shahash:
        notify.telegram(f"The current GitHub release '{ha_core_release_tag}' is available for updating")
    else:
        print("Hash does not match stable, please wait before pulling")
else:
    print(f"Current github release '{ha_core_release_tag}'' is not available as a docker")
