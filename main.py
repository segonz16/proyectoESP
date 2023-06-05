import umail
import network
import machine, onewire, ds18x20, time
import urequests

ds_pin = machine.Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
led = machine.Pin(2,machine.Pin.OUT)
led.off()

temp=''
desc=''
sw = False

roms = ds_sensor.scan()
print('Found DS devices: ', roms)

def handleSubmit():
    url = "http://192.168.1.54/urequestESP32/insertFromESP32.php"
    
    data = {
        "tempe": temp,
        "descr": desc
    }
    headers = {'Content-Type': 'application/json'}
    
    response = urequests.post(url, json=data, headers=headers)
    print(response.content)


def web_page():
  if relay.value() == 1:
    relay_state = ''
  else:
    relay_state = ''
  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
  body{font-family:Arial; text-align: center; margin: 0px auto; padding-top:30px;}
  .switch{position:relative;display:inline-block;width:120px;height:68px}.switch input{display:none}
  .slider{position:absolute;top:0;left:0;right:0;bottom:0;background-color:#ccc;border-radius:34px}
  .slider:before{position:absolute;content:"";height:52px;width:52px;left:8px;bottom:8px;background-color:#fff;-webkit-transition:.4s;transition:.4s;border-radius:68px}
  input:checked+.slider{background-color:#2196F3}
  input:checked+.slider:before{-webkit-transform:translateX(52px);-ms-transform:translateX(52px);transform:translateX(52px)}
  </style><script>function toggleCheckbox(element) { var xhr = new XMLHttpRequest(); if(element.checked){ xhr.open("GET", "/?relay=on", true); }
  else { xhr.open("GET", "/?relay=off", true); } xhr.send(); }</script></head><body>
  <h1>ESP Relay Web Server</h1><label class="switch"><input type="checkbox" onchange="toggleCheckbox(this)" %s><span class="slider">
  </span></label></body></html>""" % (relay_state)
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

contador =0
bandera = False
while True:
    if bandera == True:
        print('primer paso')
        try:
            contador +=1
            print(contador)
            if gc.mem_free() < 102000:
                gc.collect()
            conn, addr = s.accept()
            conn.settimeout(3.0)
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            conn.settimeout(None)
            request = str(request)
            print('Content = %s' % request)
            relay_on = request.find('/?relay=on')
            relay_off = request.find('/?relay=off')
            if relay_on == 6:
              print('RELAY ON')
              relay.value(1)
              while True:
                time.sleep(10)
                ds_sensor.convert_temp()
                time.sleep_ms(750)
                for rom in roms:
                    print(rom)
                    print(ds_sensor.read_temp(rom))
                temp=str(ds_sensor.read_temp(rom))
        
                if(ds_sensor.read_temp(rom)<27.9):
                    desc='Temperatura normal'
                    print(desc)
                    led.off()

                    sender_email = 'proyectoesp647@gmail.com'
                    sender_name = 'EPS32'
                    sender_app_password = 'fvugerndlgzotulv'
                    recipient_email = 'sebastian.goar159@outlook.com'
                    email_subject = 'Test Email'

                    smtp = umail.SMTP('smtp.gmail.com',465,ssl=True)
                    smtp.login(sender_email, sender_app_password)
                    smtp.to(recipient_email)
                    smtp.write("From:" + sender_name + "<" + sender_email+">\n")
                    smtp.write("Subject:" + email_subject + "\n")
                    smtp.write("Alerta!!!! Temperatura normal, apague bomba " + temp + "\n")
                    smtp.send()
                    smtp.quit()
                    bandera = True
                    time.sleep(10)
                    break
                else:
                    desc='Temperatura alta'
                    print(desc)
                    time.sleep(10)
                handleSubmit()
                
                sw = True
            if relay_off == 6:
                print('RELAY OFF')
                relay.value(0)
                bandera = False
            response = web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
    
        except OSError as e:
            conn.close()
            print('Connection closed')
        
    else:
        while True and bandera == False:
          ds_sensor.convert_temp()
          time.sleep_ms(750)
          for rom in roms:
            print(rom)
            print(ds_sensor.read_temp(rom))
          temp=str(ds_sensor.read_temp(rom))
        
          if(ds_sensor.read_temp(rom)>=28):
              desc='Temperatura alta'
              print(desc)
              led.on()
              sender_email = 'proyectoesp647@gmail.com'
              sender_name = 'EPS32'
              sender_app_password = 'fvugerndlgzotulv'
              recipient_email = 'sebastian.goar159@outlook.com'
              email_subject = 'Test Email'

              smtp = umail.SMTP('smtp.gmail.com',465,ssl=True)
              smtp.login(sender_email, sender_app_password)
              smtp.to(recipient_email)
              smtp.write("From:" + sender_name + "<" + sender_email+">\n")
              smtp.write("Subject:" + email_subject + "\n")
              smtp.write("Alerta!!!! Temperatura Alta, encienda la bomba " + temp + "\n")
              smtp.send()
              smtp.quit()
              bandera = True
              time.sleep(10)
          else:
            desc='Temperatura normal'
            print(desc)
            led.off()
            time.sleep(10)
          handleSubmit()
