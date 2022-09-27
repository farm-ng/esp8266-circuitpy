from busio import UART
from time import sleep, monotonic
from os import listdir

ESP8266_OK_STATUS = "OK\r\n"
ESP8266_ERROR_STATUS = "ERROR\r\n"
ESP8266_FAIL_STATUS = "FAIL\r\n"
ESP8266_WIFI_CONNECTED = "WIFI CONNECTED\r\n"
ESP8266_WIFI_GOT_IP_CONNECTED = "WIFI GOT IP\r\n"
ESP8266_WIFI_DISCONNECTED = "WIFI DISCONNECT\r\n"
ESP8266_WIFI_AP_NOT_PRESENT = "WIFI AP NOT FOUND\r\n"
ESP8266_WIFI_AP_WRONG_PWD = "WIFI AP WRONG PASSWORD\r\n"
ESP8266_BUSY_STATUS = "busy p...\r\n"


class ESP8266:
    """
    This is a class for access ESP8266 using AT commands
    Using this class, you access WiFi and do HTTP Post/Get operations.

    Attributes:
        uartPort (int): The Uart port numbet of the RPI Pico's UART BUS [Default UART0]
        baudRate (int): UART Baud-Rate for communncating between RPI Pico's & ESP8266 [Default 115200]
        txPin (init): RPI Pico's Tx pin [Default Pin 0]
        rxPin (init): RPI Pico's Rx pin [Default Pin 1]
    """

    def __init__(
        self, uartPort=0, baudRate=115200, txPin=(0), rxPin=(1), rx_buffer_size=2048
    ):
        """
        The constructor for ESP8266 class

        Parameters:
            uartPort (int): The UART port number of the RPI Pico's UART BUS [Default UART0]
            baudRate (int): UART Baud-Rate for communicating between RPI Pico's & ESP8266 [Default 115200]
            txPin (init): RPI Pico's Tx pin [Default Pin 0]
            rxPin (init): RPI Pico's Rx pin [Default Pin 1]
        """
        self._rx_buffer_size = rx_buffer_size
        self.__uartObj = UART(
            txPin,
            rxPin,
            baudrate=baudRate,
            receiver_buffer_size=rx_buffer_size,
        )

    def _sendToESP8266(self, atCMD, delay=0, timeout=2):
        """
        This is private function for complete ESP8266 AT command Send/Receive operation.
        """
        if isinstance(atCMD, str):
            atCMD = atCMD.encode("utf-8")
        # print("-->", atCMD)
        self.__uartObj.write(atCMD)

        sleep(delay)
        stamp = monotonic()
        while (monotonic() - stamp) < timeout:
            if self.__uartObj.in_waiting > 0:
                break

        _rxData = bytes()
        while self.__uartObj.in_waiting > 0:
            _rxData += self.__uartObj.read(self._rx_buffer_size)
        # print("<--", _rxData)

        if ESP8266_OK_STATUS in _rxData:
            return _rxData
        elif ESP8266_ERROR_STATUS in _rxData:
            return _rxData
        elif ESP8266_FAIL_STATUS in _rxData:
            return _rxData
        elif ESP8266_BUSY_STATUS in _rxData:
            return "ESP BUSY\r\n"
        else:
            return None

    def startUP(self):
        """
        This function is used to check the communication between ESP8266 & RPI Pico

        Return:
            True if communication success with the ESP8266
            False if unable to communication with the ESP8266
        """
        retData = self._sendToESP8266("AT\r\n")
        if retData != None:
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            False

    def reStart(self):
        """
        This function is used to Reset the ESP8266

        Return:
            True if Reset successfully done with the ESP8266
            False if unable to reset the ESP8266
        """
        retData = self._sendToESP8266("AT+RST\r\n")
        if retData != None:
            if ESP8266_OK_STATUS in retData:
                sleep(5)
                # self.startUP()
                return self.startUP()
            else:
                return False
        else:
            False

    def echoING(self, enable=False):
        """
        This function is used to enable/diable AT command echo [Default set as false for diable Echo]

        Return:
            True if echo off/on command succefully initiate with the ESP8266
            False if echo off/on command failed to initiate with the ESP8266

        """
        if enable == False:
            retData = self._sendToESP8266("ATE0\r\n")
            if retData != None:
                if ESP8266_OK_STATUS in retData:
                    return True
                else:
                    return False
            else:
                return False
        else:
            retData = self._sendToESP8266("ATE1\r\n")
            if retData != None:
                if ESP8266_OK_STATUS in retData:
                    return True
                else:
                    return False
            else:
                return False

    def getVersion(self):
        """
        This function is used to get AT command Version details

        Return:
            Version details on success else None
        """
        retData = self._sendToESP8266("AT+GMR\r\n")
        if retData != None:
            if ESP8266_OK_STATUS in retData:
                # print(str(retData,"utf-8"))
                retData = str(retData).partition(r"OK")[0]
                # print(str(retData,"utf-8"))
                retData = retData.split(r"\r\n")
                retData[0] = retData[0].replace("b'", "")
                retData = str(retData[0] + "\r\n" + retData[1] + "\r\n" + retData[2])
                return retData
            else:
                return None
        else:
            return None

    def reStore(self):
        """
        This function is used to reset the ESP8266 into the Factory reset mode & delete previous configurations
        Return:
            True on ESP8266 restore succesfully
            False on failed to restore ESP8266
        """
        retData = self._sendToESP8266("AT+RESTORE\r\n")
        if retData != None:
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            return None

    def getCurrentWiFiMode(self):
        """
        This function is used to query ESP8266 WiFi's current mode [STA: Station, SoftAP: Software AccessPoint, or Both]

        Return:
            STA if ESP8266's wifi's current mode pre-config as Station
            SoftAP if ESP8266's wifi's current mode pre-config as SoftAP
            SoftAP+STA if ESP8266's wifi's current mode set pre-config Station & SoftAP
            None failed to detect the wifi's current pre-config mode
        """
        retData = self._sendToESP8266("AT+CWMODE_CUR?\r\n")
        if retData != None:
            if "1" in retData:
                return "STA"
            elif "2" in retData:
                return "SoftAP"
            elif "3" in retData:
                return "SoftAP+STA"
            else:
                return None
        else:
            return None

    def setCurrentWiFiMode(self, mode=3):
        """
        This function is used to set ESP8266 WiFi's current mode [STA: Station, SoftAP: Software AccessPoint, or Both]

        Parameter:
            mode (int): ESP8266 WiFi's [ 1: STA, 2: SoftAP, 3: SoftAP+STA(default)]

        Return:
            True on successfully set the current wifi mode
            False on failed set the current wifi mode

        """
        txData = "AT+CWMODE_CUR=" + str(mode) + "\r\n"
        retData = self._sendToESP8266(txData)
        if retData != None:
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            return False

    def getDefaultWiFiMode(self):
        """
        This function is used to query ESP8266 WiFi's default mode [STA: Station, SoftAP: Software AccessPoint, or Both]

        Return:
            STA if ESP8266's wifi's default mode pre-config as Station
            SoftAP if ESP8266's wifi's default mode pre-config as SoftAP
            SoftAP+STA if ESP8266's wifi's default mode set pre-config Station & SoftAP
            None failed to detect the wifi's default pre-config mode

        """
        retData = self._sendToESP8266("AT+CWMODE_DEF?\r\n")
        if retData != None:
            if "1" in retData:
                return "STA"
            elif "2" in retData:
                return "SoftAP"
            elif "3" in retData:
                return "SoftAP+STA"
            else:
                return None
        else:
            return None

    def setDefaultWiFiMode(self, mode=3):
        """
        This function is used to set ESP8266 WiFi's default mode [STA: Station, SoftAP: Software AccessPoint, or Both]

        Parameter:
            mode (int): ESP8266 WiFi's [ 1: STA, 2: SoftAP, 3: SoftAP+STA(default)]

        Return:
            True on successfully set the default wifi mode
            False on failed set the default wifi mode

        """
        txData = "AT+CWMODE_DEF=" + str(mode) + "\r\n"
        retData = self._sendToESP8266(txData)
        if retData != None:
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            return False

    def getAvailableAPs(self):
        """
        This function is used to query ESP8266 for available WiFi AccessPoins

        Retuns:
            List of Available APs or None
        """
        retData = str(self._sendToESP8266("AT+CWLAP\r\n", delay=1, timeout=5))
        if retData != None:
            retData = list(
                retData.replace("+CWLAP:", "")
                .replace(r"\r\n\r\nOK\r\n", "")
                .replace(r"\r\n", "@")
                .replace("b'(", "(")
                .replace("\\'", "'")
                .split("@")
            )

            apLists = list()
            for items in retData:
                apLists.append(
                    tuple(str(items).replace("(", "").replace(")", "").split(","))
                )

            return apLists
        else:
            return None

    def connectWiFi(self, ssid, pwd):
        """
        This function is used to connect ESP8266 with a WiFi AccessPoins

        Parameters:
            ssid : WiFi AP's SSID
            pwd : WiFi AP's Password

        Retuns:
            WIFI DISCONNECT when ESP8266 failed connect with target AP's credential
            WIFI AP WRONG PASSWORD when ESP8266 tried connect with taget AP with wrong password
            WIFI AP NOT FOUND when ESP8266 cann't find the target AP
            WIFI CONNECTED when ESP8266 successfully connect with the target AP
        """
        txData = "AT+CWJAP_CUR=" + '"' + ssid + '"' + "," + '"' + pwd + '"' + "\r\n"
        # print(txData)
        retData = self._sendToESP8266(txData, delay=1, timeout=5)
        # print(".....")
        # print(retData)
        if retData != None:
            if "+CWJAP" in retData:
                if "1" in retData:
                    return ESP8266_WIFI_DISCONNECTED
                elif "2" in retData:
                    return ESP8266_WIFI_AP_WRONG_PWD
                elif "3" in retData:
                    return ESP8266_WIFI_AP_NOT_PRESENT
                elif "4" in retData:
                    return ESP8266_WIFI_DISCONNECTED
                else:
                    return None
            elif ESP8266_WIFI_CONNECTED in retData:
                if ESP8266_WIFI_GOT_IP_CONNECTED in retData:
                    return ESP8266_WIFI_CONNECTED
                else:
                    return ESP8266_WIFI_DISCONNECTED
            else:
                return ESP8266_WIFI_DISCONNECTED
        else:
            return ESP8266_WIFI_DISCONNECTED

    def disconnectWiFi(self):
        """
        This function is used to disconnect ESP8266 with a connected WiFi AccessPoints

        Return:
            False on failed to disconnect the WiFi
            True on successfully disconnected
        """
        retData = self._sendToESP8266("AT+CWQAP\r\n")
        if retData != None:
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            return False

    def _createTCPConnection(self, link, port=80, delay=0, timeout=2):
        """
        This function is used to create connect between ESP8266 and Host.
        Just like create a socket before complete the HTTP Get/Post operation.

        Return:
            False on failed to create a socket connection
            True on successfully create and establish a socket connection.
        """
        # self._sendToESP8266("AT+CIPMUX=0")
        txData = f'AT+CIPSTART="TCP","{link}",{str(port)}\r\n'
        retData = self._sendToESP8266(txData, delay=delay, timeout=timeout)
        if retData != None:
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            False

    def doHttpGet(
        self,
        host: str,
        path: str,
        user_agent: str = "RPi-Pico",
        port: int = 80,
        file: str = None,
        open_conn: bool = True,
        close_conn: bool = True,
    ):
        """
        This function is used to complete a HTTP Get operation

        Parameter:
            host (str): Host URL [ex: get operation URL: www.httpbin.org/ip. so, Host URL only "www.httpbin.org"]
            path (str): Get operation's URL path [ex: get operation URL: www.httpbin.org/ip. so, the path "/ip"]
            user-agent (str): User Agent Name [Default "RPi-Pico"]
            post (int): HTTP post number [Default port number 80]
            file (str): Write HTTP GET result to this file path, if given
            open_conn (bool): Whether to open TCP connection (AT+CIPSTART)
            close_conn (bool): Whether to close TCP connection (AT+CIPCLOSE)

        Return:
            HTTP error code & HTTP response[If error not equal to 200 then the response is None]
            On failed return 0 and None

        """
        if open_conn:
            connected = self._createTCPConnection(host, port, timeout=5)
        else:
            connected = True

        if connected:
            getHeader = (
                f"GET {path} HTTP/1.1\r\n"
                + f"Host: {host}\r\n"
                + f"User-Agent: {user_agent}\r\n\r\n"
            )
            txData = "AT+CIPSEND=" + str(len(getHeader)) + "\r\n"
            retData = self._sendToESP8266(txData, timeout=5)
            if retData != None:
                if ">" in retData:
                    retData = self._sendToESP8266(getHeader, timeout=5)
                    code, resp = parseHTTP(retData)
                    del retData

                    while file is not None and file[0] == "/":
                        file = file[1:]  # To find with os.listdir()

                    write_bool = (
                        resp is not None
                        and code == 200
                        and file is not None
                        and all(x in listdir() for x in ["NO_USB", file])
                    )
                    # Append file with parsed http response
                    if write_bool:
                        print("Appending file:", file)
                        f = open(file, "ab")
                        f.write(resp)
                        f.close()
                    else:
                        print("Not writing response to file:", file)
                        # print(resp)

                    if close_conn:
                        self._sendToESP8266("AT+CIPCLOSE\r\n")

                    if resp is not None:
                        return code, resp
                    else:
                        return code, None
                else:
                    return 0, None
            else:
                return 0, None
        else:
            # Close anyways if connection creation errs
            self._sendToESP8266("AT+CIPCLOSE\r\n")
            return 0, None

    def doHttpPost(self, host, path, user_agent, content_type, content, port=80):
        """
        This function is used to complete a HTTP Post operation

        Parameter:
            host (str): Host URL [ex: get operation URL: www.httpbin.org/ip. so, Host URL only "www.httpbin.org"]
            path (str): Get operation's URL path [ex: get operation URL: www.httpbin.org/ip. so, the path "/ip"]
            user-agent (str): User Agent Name [Default "RPi-Pico"]
            content_type (str): Post operation's upload content type [ex. "application/json", "application/x-www-form-urlencoded", "text/plain"
            content (str): Post operation's upload content
            post (int): HTTP post number [Default port number 80]

        Return:
            HTTP error code & HTTP response[If error not equal to 200 then the response is None]
            On failed return 0 and None

        """
        if self._createTCPConnection(host, port, timeout=5):
            postHeader = (
                "POST "
                + path
                + " HTTP/1.1\r\n"
                + "Host: "
                + host
                + "\r\n"
                + "User-Agent: "
                + user_agent
                + "\r\n"
                + "Content-Type: "
                + content_type
                + "\r\n"
                + "Content-Length: "
                + str(len(content))
                + "\r\n"
                + "\r\n"
                + content
                + "\r\n"
            )
            # print(postHeader,len(postHeader))
            txData = "AT+CIPSEND=" + str(len(postHeader)) + "\r\n"
            retData = self._sendToESP8266(txData)
            if retData != None:
                if ">" in retData:
                    retData = self._sendToESP8266(postHeader, delay=1, timeout=3)
                    self._sendToESP8266("AT+CIPCLOSE\r\n")

                    code, resp = parseHTTP(retData)
                    if resp is not None:
                        return code, resp
                    else:
                        return code, None

                else:
                    return 0, None
            else:
                return 0, None
        else:
            self._sendToESP8266("AT+CIPCLOSE\r\n")
            return 0, None

    def __del__(self):
        """
        The destructor for ESP8266 class
        """
        print("Destructor called, ESP8266 deleted.")
        pass


def parseHTTP(httpRes):
    """
    This function is used to parse the HTTP response and return back the HTTP status code
    and the parsed response

    Return:
        HTTP status code, HTTP parsed response
    """
    if httpRes != None:
        httpRes = httpRes.partition(b"+IPD,")[2].split(b"\r\n\r\n")
        header = httpRes[0].partition(b":")[2]

        for code in header.partition(b"\r\n")[0].split():
            if code.isdigit():
                __httpErrCode = int(code)
                break

        if __httpErrCode != 200:
            return __httpErrCode, None

        if httpRes[1][:6] == b"\r\n+IPD":  # Sometimes prefaces received data
            return __httpErrCode, httpRes[1].partition(b":")[2]
        else:
            return __httpErrCode, httpRes[1]
    else:
        return 0, None
