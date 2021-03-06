#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2018-2020 Ian Leonard (antonlacon@gmail.com)


# Core Modules
from datetime import datetime
# Project Modules
# OBS Modules
import obspython as obs


clock_24hr      = False
timezone_text   = ""
source_name     = ""


def set_timer_interval():
  # Clear current timer
  obs.timer_remove(update_text)
  # Set timer to be until next minute strikes; timer in milliseconds
  obs.timer_add(update_text, (60 - int(datetime.now().strftime("%S"))) * 1000)

def update_text():
  global source_name
  source = obs.obs_get_source_by_name(source_name)

  if source is not None:
    # Get the time from the computer OBS runs on
    if clock_24hr is True:
      time_now = datetime.now().strftime("%H:%M")
    else:
      time_now = datetime.now().strftime("%I:%M %p").lstrip("0")

    # Add timezone text beneath clock
    if timezone_text != "":
      clock_entry = f"{time_now}\n{timezone_text}"
    else:
      clock_entry = time_now

    # Updating the OBS source data
    settings = obs.obs_data_create()
    obs.obs_data_set_string(settings, "text", clock_entry)
    obs.obs_source_update(source, settings)
    obs.obs_data_release(settings)
    obs.obs_source_release(source)

    set_timer_interval()

def refresh_pressed(props, prop):
  update_text()

def script_description():
  return "Update a Text source to the current time.\n\nLicense: GPL-3 (https://www.gnu.org/licenses/gpl-3.0.en.html)\nCopyright (C) 2018-2020 Ian Leonard (antonlacon@gmail.com)"

def script_update(settings):
  global clock_24hr
  global timezone_text
  global source_name

  clock_24hr = obs.obs_data_get_bool(settings, "clock_24hr")
  timezone_text = obs.obs_data_get_string(settings, "timezone_text")
  source_name = obs.obs_data_get_string(settings, "source_name")

  if source_name != "":
    set_timer_interval()

def script_defaults(settings):
  obs.obs_data_set_default_bool(settings, "clock_24hr", False)
  obs.obs_data_set_default_string(settings, "timezone_text", "")
  obs.obs_data_set_default_string(settings, "source_name", "")

def script_properties():
  props = obs.obs_properties_create()

  # True/False checkbox (checked == True)
  obs.obs_properties_add_bool(props, "clock_24hr", "Use 24-hour clock")

  # Text field entry
  obs.obs_properties_add_text(props, "timezone_text", "Timezone (optional)", obs.OBS_TEXT_DEFAULT)

  # Drop down menu of Text sources
  p = obs.obs_properties_add_list(props, "source_name", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
  sources = obs.obs_enum_sources()
  if sources is not None:
    for source in sources:
      source_id = obs.obs_source_get_id(source)
      if source_id == "text_gdiplus" or source_id == "text_ft2_source":
        name = obs.obs_source_get_name(source)
        obs.obs_property_list_add_string(p, name, name)

    obs.source_list_release(sources)

  # Button in OBS script menu to interact with script
  obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)

  return props
