import network
import time

def connectar_wifi():
    # Credenciais carregadas do arquivo secrets.py (não versionado)
    try:
        from secrets import WIFI_SSID, WIFI_SENHA
        ssid  = WIFI_SSID
        senha = WIFI_SENHA
    except ImportError:
        print("ERRO: crie o arquivo Esp32/secrets.py com WIFI_SSID e WIFI_SENHA")
        return

    #sta_if(station interface) é a interface de rede sem fio do dispositivo, 
    # que é usada para se conectar a redes Wi-Fi
    sta_if = network.WLAN(network.STA_IF)
    
    # Se o wifi estiver travado em estado estranho, desativa primeiro
    sta_if.active(False)
    time.sleep(0.5)
    sta_if.active(True)
    
    #Verifica se o dispositivo já está conectado a uma rede Wi-Fi. Se não estiver, ele tenta 
    #se conectar à rede especificada pelo SSID e senha fornecidos.
    if not sta_if.isconnected():
        print("Buscando rede Wifi...")
        sta_if.connect(ssid, senha)

        #Tentativas de conexão por 10 segundos
        tentativas = 0
        while not sta_if.isconnected() and tentativas < 10:
            print(".", end="")
            time.sleep(1)
            tentativas += 1     
    
    #Após as tentativas de conexão, o código verifica se a conexão foi bem-sucedida usando 
    #sta_if.isconnected().
    if sta_if.isconnected():
        print("\nConectado com sucesso!")
        print("Configurações de rede:", sta_if.ifconfig())
    else:
        print("\nFalha ao conectar à rede Wi-Fi., Verifique as configurações")   

connectar_wifi()

