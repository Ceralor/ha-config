#!/usr/bin/env python3

## Hue Assistant for Pyscript
## CC-BY-SA Kay Ohtie, 2020
## Adds lists for Hue Bridge-stored scenes and Hue Essentials effects/animations stored in the Bridge
## This requires two Input Select helpers: Hue Animations and Hue Scenes
## This also requires an input_text named hue_user that has a valid Hue username, preferably the one your HA app uses
## It also needs the bridge's IP; I use a rate accelerator to pull this but you can manually plug it below.
## You can activate the selected scene/effect by calling pyscript.activate_scene or pyscript.activate_effect
## You can also supply room_scene or room_effect, respectively, formatted as "<Room Name> - <Scene/Effect Name>"

@time_trigger('startup')
def init_pyscript_huelists():
    pyscript.hue_lists = "ATTRIB"

@time_trigger('startup','cron(0 * * * *')
@service
def update_effects():
    import requests, json, re
    hue_info = state.getattr('sensor.hue_polling_interval')
    ## Change below to your Hue Bridge's IP if you aren't using Fast Hue Polling integration
    bridge_host = hue_info['bridge_host']
    hue_user = state.get('input_text.hue_user')
    hue_api_url = f"http://{bridge_host}/api/{hue_user}"
    groupsearch = re.compile("/groups/\d+")
    sensors = requests.get(hue_api_url+'/sensors').json()
    groups = requests.get(hue_api_url+'/groups').json()
    resourcelinks = requests.get(hue_api_url+'/resourcelinks').json()
    hue_essentials_sensors = [x for x in sensors.keys() if sensors[x]['type'] == 'CLIPGenericStatus']
    hue_effects_sensors = [x for x in hue_essentials_sensors if sensors[x]['modelid'] == 'HueEssentialsEffect_State']
    hue_effects = {}
    for effect_sensor in hue_effects_sensors:
        resourcelink = [resourcelinks[x] for x in resourcelinks.keys() if f"/sensors/{effect_sensor}" in resourcelinks[x]['links']][0]
        group_path = list(filter(groupsearch.match,resourcelink['links']))[0]
        group_id = re.search("(\d+)",group_path).group(1)
        group = groups[group_id]
        effect_display_name = group['name'] + " - " + resourcelink['name']
        log.debug(f"Storing info for effect {effect_display_name}")
        hue_effects[effect_display_name] = effect_sensor
    state.setattr('pyscript.hue_lists.effects_json', json.dumps(hue_effects))
    input_select.set_options(options=list(hue_effects.keys()),entity_id="input_select.hue_animations")

@time_trigger('startup','cron(0 * * * *')
@service
def update_scenes():
    import requests, json
    hue_info = state.getattr('sensor.hue_polling_interval')
    bridge_host = hue_info['bridge_host']
    hue_user = state.get('input_text.hue_user')
    hue_api_url = f"http://{bridge_host}/api/{hue_user}"
    groups = requests.get(hue_api_url+'/groups').json()
    scenes = requests.get(hue_api_url+'/scenes').json()
    hue_scenes = {}
    for scene_id in scenes.keys():
        scene = scenes[scene_id]
        if scene['name'] == 'HueEssentialsEffect':
            continue
        group = groups[scene['group']]
        scene_display_name = f"{group['name']} - {scene['name']}"
        log.debug(f"Storing info for scene {scene_display_name}")
        hue_scenes[scene_display_name] = {'scene_name':scene['name'],'scene_id':scene_id,'group_name':group['name'],'group_id':scene['group']}
    state.setattr('pyscript.hue_lists.scenes_json',json.dumps(hue_scenes))
    input_select.set_options(options=list(hue_scenes.keys()),entity_id="input_select.hue_scenes")

@service
def activate_scene(room_scene=None):
    import requests, json
    if room_scene == None:
        room_scene = input_select.hue_scenes
    scenes = json.loads(state.getattr('pyscript.hue_lists')['scenes_json'])
    if room_scene not in scenes.keys():
        update_scenes()
        scenes = json.loads(state.getattr('pyscript.hue_lists')['scenes_json'])
        if room_scene not in scenes.keys():
            log.error(f"{room_scene} not found in Hue Bridge")
            return False
    scene_info = scenes[room_scene]
    log.debug(f"Activating '{scene_info['scene_name']}'' in '{scene_info['group_name']}'")
    hue.hue_activate_scene(group_name=scene_info['group_name'],scene_name=scene_info['scene_name'])

def send_sensor_state(sensor_id=None,state_name=None,state_value=None):
    import requests, json
    hue_info = state.getattr('sensor.hue_polling_interval')
    bridge_host = hue_info['bridge_host']
    hue_user = state.get('input_text.hue_user')
    hue_api_url = f"http://{bridge_host}/api/{hue_user}"
    body = {state_name: state_value}
    r = requests.put(hue_api_url+f"/sensors/{sensor_id}/state",json=body)
    if r.status_code == 200:
        log.debug(f"Successfully set {state_name} to {state_value} on sensor ID {sensor_id}")
    else:
        log.error(r.text)
        return False

@service
def activate_effect(room_effect=None):
    import requests, json
    hue_info = state.getattr('sensor.hue_polling_interval')
    bridge_host = hue_info['bridge_host']
    hue_user = state.get('input_text.hue_user')
    hue_api_url = f"http://{bridge_host}/api/{hue_user}"
    if room_effect == None:
        room_effect = input_select.hue_animations
    effects = json.loads(state.getattr('pyscript.hue_lists')['effects_json'])
    if room_effect not in effects.keys():
        update_effects()
        effects = json.loads(state.getattr('pyscript.hue_lists')['effects_json'])
        if room_effect not in effects.keys():
            log.error(f"{room_effect} not found in Hue Bridge")
            return False
    effect_sensor_id = effects[room_effect]
    deactivate_effects()
    send_sensor_state(effect_sensor_id,'status',1)

@service
def deactivate_effects():
    import requests, json
    hue_info = state.getattr('sensor.hue_polling_interval')
    bridge_host = hue_info['bridge_host']
    hue_user = state.get('input_text.hue_user')
    hue_api_url = f"http://{bridge_host}/api/{hue_user}"
    effects = json.loads(state.getattr('pyscript.hue_lists')['effects_json'])
    for effect_id in effects.values():
        send_sensor_state(effect_id,'status',0)
