from neopixel.neopixel import Neopixel

class Touch():
    def __init__(self, touch_sensor):
        self.touch_sensor = touch_sensor.value()        
        
    def status(self):
        if self.touch_sensor == 1:
            touch_status = True
        elif self.touch_sensor == 0:
            touch_status = False
        return touch_status


class LedStrip(Neopixel):
    def __init__(self, num_leds, state_machine, pin, is_on, color_hs, brightness, mode="GRB", delay=0.0001):
        super().__init__(num_leds, state_machine, pin, mode="GRB", delay=0.0001)
        self.color_hs = color_hs
        self.brightness_level = brightness
        self.is_on = is_on
        self.color_hsv = None
        self.color_rgb = None
        
        
    def hsv_to_rgb(self, hsv_values):
        rgb = self.colorHSV(self.color_hsv[0], self.color_hsv[1], self.color_hsv[2])
        return rgb
    
    def status(self):
        if self.is_on == True:
            status = 'ON'
        elif self.is_on == False: 
            status = 'OFF'        
        return status
              
    def change_brightness(self, brightness):
        self.brightness_level = brightness
        self.color_hsv = (self.color_hs[0], self.color_hs[1], self.brightness_level)
        self.color_rgb = self.hsv_to_rgb(self.color_hsv)
        self.fill(self.color_rgb)
        self.show()
        return self.brightness_level
           
    def on(self):
        self.is_on = True
        self.color_hsv = (self.color_hs[0], self.color_hs[1], self.brightness_level)
        self.color_rgb = self.hsv_to_rgb(self.color_hsv)
        self.fill(self.color_rgb)
        self.show()
        return self.is_on
        
    def off(self):
        self.is_on = False
        self.fill((0, 0, 0))
        self.show()
        return self.is_on

    def toggle(self):
        if self.is_on:
            self.off()
        else:
            self.on()
        return self.is_on
    
    def change_color(self, color):        
        self.color_hs = (color[0], color[1])
        self.on()
        return self.color_hs
    
    def decrease_brightness(self, brightness):
        if brightness <= 102:
            self.brightness_level = 51
        else:
            self.brightness_level = brightness - 51
        self.change_brightness(self.brightness_level)
        return self.brightness_level
    
    def increase_brightness(self, brightness):
        if brightness >= 204:
            self.brightness_level = 255
        else:
            self.brightness_level = brightness + 51
        self.change_brightness(self.brightness_level)
        return self.brightness_level
    
def next_color(current_color, colors_list):
    color_index = colors_list.index(current_color)
    next_color_index = color_index + 1
    
    if next_color_index == len(colors_list):
        next_color = colors_list[0]
    else:
        next_color = colors_list[next_color_index]
    
    return next_color
    
def normalize_hsv(h, s, v):
    hue = h * 182
    saturation = s * 2.55
    hsv = (int(hue), int(saturation), v)
    return hsv
