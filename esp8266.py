# from machine import UART, Pin
from busio import UART
from microcontroller import pin
from time import sleep, monotonic
from os import listdir
from gc import collect as gc_collect

ESP8266_OK_STATUS = "OK\r\n"
ESP8266_ERROR_STATUS = "ERROR\r\n"
ESP8266_FAIL_STATUS = "FAIL\r\n"
ESP8266_WIFI_CONNECTED = "WIFI CONNECTED\r\n"
ESP8266_WIFI_GOT_IP_CONNECTED = "WIFI GOT IP\r\n"
ESP8266_WIFI_DISCONNECTED = "WIFI DISCONNECT\r\n"
ESP8266_WIFI_AP_NOT_PRESENT = "WIFI AP NOT FOUND\r\n"
ESP8266_WIFI_AP_WRONG_PWD = "WIFI AP WRONG PASSWORD\r\n"
ESP8266_BUSY_STATUS = "busy p...\r\n"
UART_Tx_BUFFER_LENGTH = 1024
UART_Rx_BUFFER_LENGTH = 1024 * 2


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

    __rxData = None
    __txData = None

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

    def _sendToESP8266(self, atCMD, delay=1, timeout=1):
        """
        This is private function for complete ESP8266 AT command Send/Receive operation.
        """
        if isinstance(atCMD, str):
            atCMD = atCMD.encode("utf-8")
        # self.__rxData=str()
        self.__rxData = bytes()
        self.__txData = atCMD
        # print("---------------------------"+self.__txData)
        print("-->", self.__txData)
        self.__uartObj.write(self.__txData)

        sleep(delay)

        # while self.__uartObj.any()>0:
        #    self.__rxData += self.__uartObj.read(1)

        stamp = monotonic()
        while (monotonic() - stamp) < timeout:
            # print(".")
            # if self.__uartObj.any()>0:
            if self.__uartObj.in_waiting > 0:
                # print(self.__uartObj.any())
                break

        while self.__uartObj.in_waiting > 0:
            rx = self.__uartObj.read(UART_Rx_BUFFER_LENGTH)
            print("CHUNK:", type(rx), type(self.__rxData))
            print("<--", rx)
            self.__rxData += rx

        # print("<--", self.__rxData)
        # print(self.__rxData)
        if ESP8266_OK_STATUS in self.__rxData:
            return self.__rxData
        elif ESP8266_ERROR_STATUS in self.__rxData:
            return self.__rxData
        elif ESP8266_FAIL_STATUS in self.__rxData:
            return self.__rxData
        elif ESP8266_BUSY_STATUS in self.__rxData:
            return "ESP BUSY\r\n"
        else:
            return None

    def startUP(self):
        """
        This funtion use to check the communication between ESP8266 & RPI Pico

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
        This funtion use to Reset the ESP8266

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

    """
    def chcekSYSRAM(self):
        #retData = self._sendToESP8266("AT+SYSRAM?\r\n")
        self.__rxData=b''
        self.__txData="AT+SYSRAM?\r\n"
        self.__uartObj.write(self.__txData)
        self.__rxData=bytes()

        time.sleep(2)

        while self.__uartObj.any()>0:
            self.__rxData += self.__uartObj.read(1)

        print(self.__rxData.decode())
        if ESP8266_OK_STATUS in self.__rxData:
            return self.__rxData
        else:
            return 1
    """

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

    def _createTCPConnection(self, link, port=80, delay=1, timeout=1):
        """
        This function is used to create connect between ESP8266 and Host.
        Just like create a socket before complete the HTTP Get/Post operation.

        Return:
            False on failed to create a socket connection
            True on successfully create and establish a socket connection.
        """
        # self._sendToESP8266("AT+CIPMUX=0")
        txData = (
            "AT+CIPSTART="
            + '"'
            + "TCP"
            + '"'
            + ","
            + '"'
            + link
            + '"'
            + ","
            + str(port)
            + "\r\n"
        )
        retData = self._sendToESP8266(txData, delay=delay, timeout=timeout)
        if retData != None:
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            False

    def doHttpGet(self, host, path, user_agent="RPi-Pico", port=80):
        """
        This function is used to complete a HTTP Get operation

        Parameter:
            host (str): Host URL [ex: get operation URL: www.httpbin.org/ip. so, Host URL only "www.httpbin.org"]
            path (str): Get operation's URL path [ex: get operation URL: www.httpbin.org/ip. so, the path "/ip"]
            user-agent (str): User Agent Name [Default "RPi-Pico"]
            post (int): HTTP post number [Default port number 80]

        Return:
            HTTP error code & HTTP response[If error not equal to 200 then the response is None]
            On failed return 0 and None

        """
        if self._createTCPConnection(host, port) == True:
            self._createHTTPParseObj()
            # getHeader="GET "+path+" HTTP/1.1\r\n"+"Host: "+host+":"+str(port)+"\r\n"+"User-Agent: "+user_agent+"\r\n"+"\r\n";
            getHeader = (
                "GET "
                + path
                + " HTTP/1.1\r\n"
                + "Host: "
                + host
                + "\r\n"
                + "User-Agent: "
                + user_agent
                + "\r\n"
                + "\r\n"
            )
            # print(getHeader,len(getHeader))
            txData = "AT+CIPSEND=" + str(len(getHeader)) + "\r\n"
            retData = self._sendToESP8266(txData, delay=2, timeout=10)
            if retData != None:
                if ">" in retData:
                    retData = self._sendToESP8266(getHeader, delay=1, timeout=3)
                    if close_conn:
                        self._sendToESP8266("AT+CIPCLOSE\r\n")

                    code, resp = parseHTTP(retData)
                    if resp is not None:
                        return code, resp.encode("utf-8")
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

    # def doHttpPost(self,host,path,user_agent="RPi-Pico",content_type,content,port=80):
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
        if self._createTCPConnection(host, port) == True:
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
                        return code, resp.encode("utf-8")
                    else:
                        return code, None

                else:
                    return 0, None
            else:
                return 0, None
        else:
            self._sendToESP8266("AT+CIPCLOSE\r\n")
            return 0, None

    def doAppendingHttpGet(
        self, host, base_path, count, user_agent="RPi-Pico", port=80, file=None
    ):
        """
        This function is used to complete a HTTP Get operation

        Parameter:
            host (str): Host URL [ex: get operation URL: www.httpbin.org/ip. so, Host URL only "www.httpbin.org"]
            path (str): Get operation's URL path [ex: get operation URL: www.httpbin.org/ip. so, the path "/ip"]
            user-agent (str): User Agent Name [Default "RPi-Pico"]
            post (int): HTTP post number [Default port number 80]

        Return:
            HTTP error code & HTTP response[If error not equal to 200 then the response is None]
            On failed return 0 and None

        """
        assert file is not None

        if self._createTCPConnection(host, port, timeout=5) == True:
            # Create blank file
            if "NO_USB" in listdir():
                print("Creating / overwriting file named:", file)
                f = open(file, "w")
                f.close()
                print("created file")
            else:
                print("Add 'NO_USB' file to allow writing to filesystem")

            i = 0
            while i < count:
                gc_collect()
                getHeader = (
                    f"GET {base_path}{i:03d} HTTP/1.1\r\n"
                    + f"Host: {host}\r\n"
                    + f"User-Agent: {user_agent}\r\n\r\n"
                )

                txData = "AT+CIPSEND=" + str(len(getHeader)) + "\r\n"
                retData = self._sendToESP8266(txData, delay=0, timeout=2)
                if retData != None:
                    if ">" in retData:
                        # try:
                        ret = self._send_and_append(
                            getHeader, delay=0, timeout=3, file=file
                        )
                        if not ret:
                            print(f"Error on chunk {i:03d}! Cancelling download")
                            break
                        i += 1
                        # except:
                        #     pass
                    else:
                        print("Try again -- no '>'")
                else:
                    print("Try again - bad CIPSEND response")

        else:
            self._sendToESP8266("AT+CIPCLOSE\r\n")

    def _send_and_append(self, atCMD, delay=0, timeout=1, file=None):
        """
        This is private function for complete ESP8266 AT command Send/Receive operation.
        """
        assert file is not None

        if isinstance(atCMD, str):
            atCMD = atCMD.encode("utf-8")
        rx = bytes()

        print("-->", atCMD)
        self.__uartObj.write(atCMD)

        sleep(delay)
        stamp = monotonic()
        while (monotonic() - stamp) < timeout:
            if self.__uartObj.in_waiting > 0:
                break

        total_size = 0
        while self.__uartObj.in_waiting > 0:
            rx = self.__uartObj.read(self._rx_buffer_size)
            print("CHUNK size:", len(rx))
            total_size += len(rx)
            print("<--", rx)

            code, resp = parseHTTP(rx)
            print("code:", code)
            print("resp", len(resp), "\n", resp)
            if code != 200:
                print("Error code from http response")
                return False

            if "NO_USB" in listdir():
                with open(file, "ab") as f:
                    f.write(resp)
            else:
                print("Add 'NO_USB' file to allow writing to filesystem")
        return True

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
    # print(">>>>",httpRes)
    if httpRes != None:
        # try:
        httpRes = str(httpRes).partition("+IPD,")[2].split(r"\r\n\r\n")
        # print(">>>>>>>>>>>>>>>>>", retParseResponse)
        __httpResponse = httpRes[1]
        # print(">>>>>>>>>>>>>>>>>???", retParseResponse[1])
        __httpHeader = str(httpRes[0]).partition(":")[2]
        del httpRes
        # print("--", self.__httpHeader)
        for code in str(__httpHeader.partition(r"\r\n")[0]).split():
            if code.isdigit():
                __httpErrCode = int(code)

        if __httpErrCode != 200:
            __httpResponse = None

        return __httpErrCode, __httpResponse
        # except:
        #     print("Failed HTTP parse")
        #     return 0, None
    else:
        return 0, None
