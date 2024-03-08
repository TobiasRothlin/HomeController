from HomeController import HomeController
import time



homeController = HomeController()

counter = 0

while counter < 10:
    temp = homeController.get_temperature()
    hum = homeController.get_humidity()
    lux = homeController.get_light()
    print(lux)
    homeController.write_lcd(f"T:{temp:.2f} H:{hum:.2f} L:{lux}")

    time.sleep(0.1)
    counter += 1
    print(counter)