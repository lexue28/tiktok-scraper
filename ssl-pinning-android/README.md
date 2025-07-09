# How to do SSL Pinning in Android

## 1. Requirements

### "Big Files"

- `tiktok-v37.0.4.apk`
- `frida-server-16.6.1-android-arm64`

download them here:

- https://drive.google.com/drive/folders/1bOzVosku5jeXMJ0m6JR4lBIjgvzCBkKX?usp=sharing

### Frida
```bash
pip install -U frida-tools
```

### Android Studio SDK
https://developer.android.com/studio/install

### mitmproxy
https://docs.mitmproxy.org/stable/overview-installation/

if you have `brew` installed, you can install mitmproxy by running:
```
brew install mitmproxy
```

## 2. Steps

### Android Studio SDK

1. Open Android Studio
2. Select `Device Manager`
3. Select `+` to add a new device

Here you need to find a device that has no Play Store services installed. e.g. `Pixel 6 Pro`

4. Select the device and click `Next`
5. Select VanillaIceCream - 35 - arm64-v8a - - Android 15.0 (Google APIs)
6. Run the device

### Install apk

1. The APK is `tiktok-v37.0.4.apk`
2. Just copy paste the apk to the device
3. If needed, look at this repository for a newer version: https://github.com/Eltion/Tiktok-SSL-Pinning-Bypass
4. Run the apk and login with a TikTok account
   
### Frida

1. Switch to root adb mode
```bash
adb root
```

2. Push the frida server to the device
```bash
adb push frida-server-16.6.1-android-arm64 /data/local/tmp/frida-server
```

3. Run the frida server
```bash
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
```

4. In another terminal, run the frida client
```bash
frida -U -l tiktok-ssl-pinning-bypass.js -f com.zhiliaoapp.musically
```

5. Make sure the frida client is running and the frida server is running
You should see something like this:
```
     ____
    / _  |   Frida 16.6.5 - A world-class dynamic instrumentation toolkit
   | (_| |
    > _  |   Commands:
   /_/ |_|       help      -> Displays the help system
   . . . .       object?   -> Display information about 'object'
   . . . .       exit/quit -> Exit
   . . . .
   . . . .   More info at https://frida.re/docs/home/
   . . . .
   . . . .   Connected to Android Emulator 5554 (id=emulator-5554)
Spawning `com.zhiliaoapp.musically`...
[*][*] Waiting for libttboringssl...
Spawned `com.zhiliaoapp.musically`. Resuming main thread!
[Android Emulator 5554::com.zhiliaoapp.musically ]-> [*][+] Hooked checkTrustedRecursive
[*][+] Hooked SSLContextInit
[*][+] Found libttboringssl at: 0x7844c95000
[*][+] Hooked function: SSL_CTX_set_custom_verify
```

### mitmproxy

1. Run the mitmproxy
```bash
mitmproxy --listen-host 0.0.0.0
```

2. In the device, go to `Settings` -> `Network`
3. In the connected 'WiFi' network, click on the edit button
4. In the `Proxy` section, select `Manual`
5. Enter the IP address of your machine in the local network, e.g. `192.168.1.2`. Use the mitmproxy port, e.g. `8080`
6. Click `Save`


### You should be able to see the requests in mitmproxy


## Optional: Parse the output

1. Run mitmproxy with the `parse_output.py` script to parse the output into a file
```bash
mitmdump --listen-host 0.0.0.0 -s ssl-pinning-android/parse_output.py
```
