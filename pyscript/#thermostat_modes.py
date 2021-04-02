#!/usr/bin/env python3

@service
def thermostat_away():
	away_setpoint = 0
	if climate.thermostat == "heat":
		away_setpoint = input_number.thermostat_away_mode_heat
		switch.schedule_heat_weekdays.turn_off()
		switch.schedule_heat_weekend.turn_off()
	elif climate.thermostat == "cool":
		away_setpoint = input_number.thermostat_away_mode_cool
		switch.schedule_cooling.turn_off()
	else:
		log.warn("Current thermostat mode unsupported")
		return
	climate.thermostat.set_temperature(temperature=away_setpoint)

@service
def thermostat_home():
	if climate.thermostat == "heat":
		switch.schedule_heat_weekdays.turn_on()
		switch.schedule_heat_weekend.turn_on()
	elif climate.thermostat == "cool":
		switch.schedule_cooling.turn_on()
	else:
		log.warn("Current thermostat mode unsupported")

@state_trigger("climate.thermostat")
@time_trigger("startup")
@service
def toggle_thermostat_schedules():
	if climate.thermostat == "heat":
		switch.schedule_heat_weekdays.turn_on()
		switch.schedule_heat_weekend.turn_on()
		switch.schedule_cooling.turn_off()
	elif climate.thermostat == "cool":
		switch.schedule_heat_weekdays.turn_off()
		switch.schedule_heat_weekend.turn_off()
		switch.schedule_cooling.turn_on()
	else:
		if climate.thermostat != "off":
			log.warn("Unsupported mode, turning off schedules")
		switch.schedule_heat_weekdays.turn_off()
		switch.schedule_heat_weekend.turn_off()
		switch.schedule_cooling.turn_off()
