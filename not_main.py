import utime
import ujson
import secrets
import uasyncio
from machine import Pin
from mm_wlan import mm_wlan
from umqtt.robust import MQTTClient
from control import Touch, LedStrip, normalize_hsv, next_color

STATUS_LED = Pin(25, Pin.OUT)

TOUCH_POWER_PIN = Pin(2, Pin.IN)
TOUCH_COLOR_PIN = Pin(3, Pin.IN)
TOUCH_HIGH_PIN = Pin(4, Pin.IN)
TOUCH_LOW_PIN = Pin(5, Pin.IN)

LED_STRIP_PIN = 15
LED_LIGHT_LENGHT = 30
LED_STRIP_STATE_MACHINE = 0

IS_LIGHT_ON = False
BRIGHTNESS = 255
COLORS_LIST = [(0, 255), (20000, 255), (40000, 255)]
COLOR = COLORS_LIST[0]


MQTT_CLIENT_NAME = secrets.MQTT_CLIENT_NAME
MQTT_TOPIC_STATUS = f'{MQTT_CLIENT_NAME}/light/status'.encode()
MQTT_TOPIC_COMMAND = f'{MQTT_CLIENT_NAME}/light/command'.encode()


light = LedStrip(num_leds=LED_LIGHT_LENGHT, state_machine=LED_STRIP_STATE_MACHINE, pin=LED_STRIP_PIN, is_on=IS_LIGHT_ON, color_hs=COLOR, brightness=BRIGHTNESS)
light.off()

try:
    mm_wlan.connect_to_network(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
except:
    utime.sleep(180)
    mm_wlan.connect_to_network(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)

mqtt_client = MQTTClient(client_id=MQTT_CLIENT_NAME, server=secrets.MQTT_SERVER_IP,
                         user=secrets.MQTT_SERVER_USER, password=secrets.MQTT_SERVER_PASSWORD, keepalive=60)
mqtt_client.connect()
mqtt_client.DEBUG = True


def sub_action(topic, msg):
    global COLOR, IS_LIGHT_ON, BRIGHTNESS

    data = ujson.loads(msg)
    
    print(data)
    print(data)
    print(data)
    print(data)

    for k, v in data.items():
        if k == 'state':
            status = v
            if status == 'ON':
                IS_LIGHT_ON = light.on()
            elif status == 'OFF':
                IS_LIGHT_ON = light.off()
        elif k == 'color':
            color = v
            h = color['h']
            s = color['s']
            color_hsv = normalize_hsv(h, s, BRIGHTNESS)
            light.change_color(color_hsv)
        elif k == 'brightness':
            BRIGHTNESS = v
            light.change_brightness(BRIGHTNESS)


async def mqqt_client():

    mqtt_client.set_callback(sub_action)
    mqtt_client.subscribe(MQTT_TOPIC_COMMAND)

    while True:

        state = {"state": light.status(), "brightness": BRIGHTNESS}
        state_json = ujson.dumps(state)

        mqtt_client.publish(MQTT_TOPIC_STATUS, state_json)
        mqtt_client.check_msg()
        print('msg published')

        await uasyncio.sleep_ms(500)


async def normal():
    global COLOR, IS_LIGHT_ON, BRIGHTNESS

    while True:

        touch_power = Touch(TOUCH_POWER_PIN)
        touch_color = Touch(TOUCH_COLOR_PIN)
        touch_high = Touch(TOUCH_HIGH_PIN)
        touch_low = Touch(TOUCH_LOW_PIN)
        

        if not touch_power.status() and not touch_color.status() and not touch_low.status() and not touch_high.status():
            is_not_touched = True

        print('---Main LOOP---')

        while is_not_touched:

            print('---TOUCH LOOP---')
            print(BRIGHTNESS)
            touch_power = Touch(TOUCH_POWER_PIN)
            touch_color = Touch(TOUCH_COLOR_PIN)
            touch_high = Touch(TOUCH_HIGH_PIN)
            touch_low = Touch(TOUCH_LOW_PIN)

            if touch_power.status():
                is_not_touched = False
                IS_LIGHT_ON = light.toggle()

            if IS_LIGHT_ON:
                if touch_color.status():
                    is_not_touched = False
                    COLOR = next_color(COLOR, COLORS_LIST)
                    light.change_color(COLOR)
                    
                if touch_high.status():
                    is_not_touched = False
                    BRIGHTNESS = light.increase_brightness(BRIGHTNESS)

                if touch_low.status():
                    is_not_touched = False
                    BRIGHTNESS = light.decrease_brightness(BRIGHTNESS)                  

            await uasyncio.sleep_ms(100)
        await uasyncio.sleep_ms(100)


async def main():
    uasyncio.create_task(normal())
    await mqqt_client()


uasyncio.run(main())
