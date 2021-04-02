#!/usr/bin/env python3

@state_trigger("binary_sensor.kitchen_motion_sensor == 'off'",state_hold=60*int(float(input_number.kitchen_light_timeout)))
def turn_off_kitchen():
	light.kitchen_lights.turn_off()

@state_trigger("binary_sensor.kitchen_motion_sensor == 'on'")
def turn_on_kitchen():
	brightness_pct = 100
	color_temp = 4000
	if input_boolean.sleeping == "on":
		brightness_pct = 5
		color_temp = 2500
	light.kitchen_lights.turn_on(brightness_pct=brightness_pct,kelvin=color_temp)

@state_trigger("input_boolean.sleeping")
def check_lighting():
	if light.kitchen_lights == "on":
		turn_on_kitchen()

@state_trigger("input_number.kitchen_light_timeout")
def reload_kitchen():
	pyscript.reload(global_ctx="file.kitchen_lights")
