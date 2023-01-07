import socket, threading, base64, hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

f = open("passw.txt", "r")#passw.txt okuma modunda açılır
passwd = f.read()#dosya okunur
__key__ = hashlib.sha256(passwd.encode()).digest()#verilen sifreye göre anahtar oluşturulur


isim = str(input("isminiz: "))#isim istenir

def encrypt(raw):#sifreleme icin
    BS = AES.block_size#https://www.dlitz.net/software/pycrypto/api/2.6/Crypto.Cipher.AES-module.html
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

    raw = base64.b64encode(pad(raw).encode('utf8'))#base64 kullanılarak lambda fonksiyonundan çıkan sonuç encode edilir
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key= __key__, mode= AES.MODE_CFB,iv= iv)
    return base64.b64encode(iv + cipher.encrypt(raw))#sifrelenmis veri döndurulur

def decrypt(enc):#sifrenmis veriyi cözmek icin
    unpad = lambda s: s[:-ord(s[-1:])]

    enc = base64.b64decode(enc)#sifrelenmis veri base64 ile decode edilir geriye aesi çözmek kalır
    iv = enc[:AES.block_size]
    cipher = AES.new(__key__, AES.MODE_CFB, iv)
    return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf8'))#cozulen veri döndurulur

def handle_messages(connection: socket.socket):
    #genel amacı diğer clientlerden gelen mesajları almaktır
    while True:
        try:
            msg = connection.recv(1024)#diğer clientten gelen mesaj alınır

            if msg:#mesaj varsa
                print(decrypt(msg))#sifreli mesaj cozulur ve print edilir
            else:
                connection.close()#bağlantı sonlandırılır
                break#döngü sonlandırılır

        except Exception as e:#bir hata durumunda
            print(f'Error handling message from server: {e}')#hata yazdırılır
            connection.close()#bağlantı sonlandırılır
            break#döngü sonlandırılır

def client() -> None:
    #servera bağlanmak için ayarlar yapılır ve bağlantı gönderilir

    SERVER_ADDRESS = '127.0.0.1'#ip ayarlanır
    SERVER_PORT = 12000#port belirtilir

    try:
        socket_instance = socket.socket()#soket açılır
        socket_instance.connect((SERVER_ADDRESS, SERVER_PORT))#belirtilen ip ve porta bağlantı gönderilir

        threading.Thread(target=handle_messages, args=[socket_instance]).start()#mesaj alımı için thread başlatılır

        print('Connected to chat!')

        while True:
            msg = input("")#kullanıcının mesaj gönderebilmesi için input alınır
            msg = isim + ":" + msg#isim mesajın yanına eklenir mesela (berat: merhaba) şeklinde
            encryptedMessage = encrypt(msg)#mesaj sifrelenir edilir

            if msg == isim + ":" + "quit":#eger mesaj quit ise
                break#döngü durur

            socket_instance.send(encryptedMessage)#sifrelenmis mesaj gonderilir

        socket_instance.close()

    except Exception as e:
        print(f'Error connecting to server socket {e}')
        socket_instance.close()#bir sorun durumunda bağlantı kapatılır


client()#client fonksiyonu başlatılır